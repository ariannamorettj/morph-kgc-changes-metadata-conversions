import pandas as pd
from src.morph_kgc.__init__ import materialize
import configparser
from rdflib import Graph, Namespace, URIRef, BNode, Literal
import os
from ruamel.yaml import YAML
import re

# Percorso del file di configurazione
config_path = "src/morph_kgc_changes_metadata_conversions/config.ini"

# Creazione di un oggetto ConfigParser
config = configparser.ConfigParser()
config.read(config_path)
csv_file_path = config["DataSource1"]["file_path"]
print(f"Il valore di file_path per DataSource1 è: {csv_file_path}")

# Caricamento e pulizia CSV
df = pd.read_csv(csv_file_path, delimiter=',', quotechar='"', encoding='utf-8')
df = df.fillna('').applymap(lambda x: str(x) if pd.notna(x) else '')
df.to_csv(csv_file_path, index=False, quoting=1, encoding='utf-8')

# Percorso temporaneo della nuova configurazione
config_path_tmp = config_path.replace(".ini", "_tmp.ini")
config_tmp = configparser.ConfigParser()
config_tmp["DataSource1"] = config["DataSource1"]
input_filepath = config_tmp["DataSource1"]["file_path"]
config_tmp["CONFIGURATION"] = config["CONFIGURATION"]
base_output_dir = config["CONFIGURATION"]["output_dir"]
sub_output_dir = os.path.join(base_output_dir, "object_dataset")
config_tmp["CONFIGURATION"]["output_dir"] = sub_output_dir

# Pulizia colonne del CSV
df = pd.read_csv(input_filepath)
df.columns = [col.replace('\n', ' ').replace('  ', ' ') for col in df.columns]
df = df.fillna('').applymap(lambda x: str(x) if pd.notna(x) else '')
df.to_csv(input_filepath, index=False, quoting=1, encoding='utf-8')

if not os.path.exists(sub_output_dir):
    os.makedirs(sub_output_dir)

# Salva nuovo file di configurazione temporanea
with open(config_path_tmp, "w") as file:
    config_tmp.write(file)

# Materializzazione del grafo
try:
    graph = materialize(config_path_tmp)
except Exception as e:
    print(f"Errore durante la materializzazione: {e}")
    graph = None

# Serializzazione Turtle
output_file = config_tmp['CONFIGURATION']['output_file']
output_dir = config_tmp['CONFIGURATION']['output_dir']
output_path = os.path.join(output_dir, output_file)
if not isinstance(graph, Graph):
    raise TypeError("Expected morph_kgc.materialize to return an rdflib.Graph object")

yaml = YAML(typ='safe', pure=True)
map_file = config['DataSource1']['mappings']
with open(map_file, 'r', encoding='utf-8') as file:
    yarrrml_data = yaml.load(file)
prefixes = yarrrml_data.get('prefixes', {})
for prefix, uri in prefixes.items():
    graph.bind(prefix, Namespace(uri))
serialization = config['CONFIGURATION']['output_serialization']
graph.serialize(destination=output_path, format=serialization)

# Post-processing Turtle RDF
with open(output_path, 'r') as f:
    data = f.read()

output_file_path = output_path.replace(".ttl", "_corretto.ttl")

def extract_prefixes(text):
    return re.findall(r'@prefix\s([^\s:]+:)\s', text)

def generate_prefix_regex(prefixes):
    prefix_pattern = "|".join(re.escape(prefix) for prefix in prefixes)
    return rf'"({prefix_pattern})[^"]*"'

def remove_angular_brackets(uri):
    return uri.strip('<>')

def remove_apices(string):
    return string.strip('"')

def remove_angular_apices_add_angular_brackets(uri):
    uri = remove_apices(uri)
    if uri.startswith("<") and uri.endswith(">"):
        return uri
    elif uri.startswith("<") and not uri.endswith(">"):
        return uri +">"
    elif not uri.startswith("<") and uri.endswith(">"):
        return "<"+uri
    else:
        return "<"+uri+">"

def process_rdf_data(data):
    prefixes = extract_prefixes(data)
    string_pattern = re.compile(generate_prefix_regex(prefixes))
    uri_pattern = re.compile(r'<(?!http|https)([^>]+)>')
    bad_form_uri_pattern = re.compile(r"(?:[\"]<?)(https?:\/\/[^\s\"'<>\]]+)(?:>[\"]|[\">?])")

    def replace_uri(match): return remove_angular_brackets(match.group(0))
    def replace_badform_uri(match): return remove_angular_apices_add_angular_brackets(match.group(0))
    def replace_str(match): return remove_apices(match.group(0))

    processed_data = uri_pattern.sub(replace_uri, data)
    processed_data = string_pattern.sub(replace_str, processed_data)
    processed_data = bad_form_uri_pattern.sub(replace_badform_uri, processed_data)

    return processed_data

processed_data = process_rdf_data(data)
with open(output_file_path, 'w') as f:
    f.write(processed_data)

if os.path.exists(config_path_tmp):
    os.remove(config_path_tmp)