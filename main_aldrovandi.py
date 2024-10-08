import pandas as pd
# import morph_kgc
from src.morph_kgc.__init__ import materialize
import configparser
from rdflib import Graph, Namespace, URIRef, BNode, Literal
import os
from ruamel.yaml import YAML
import re

# caricamento CSV
csv_file_path = "src/morph_kgc_changes_metadata_conversions/output_dir/cleaned_sample.csv"
df = pd.read_csv(csv_file_path, delimiter=',', quotechar='"', encoding='utf-8')

# NaN sostituiti con stringhe vuote
df = df.fillna('')

# tutte le colonne in stringa
df = df.applymap(lambda x: str(x) if pd.notna(x) else '')

# sovrascrivere dataframe nuovo su file input
preprocessed_csv_file_path = "src/morph_kgc_changes_metadata_conversions/output_dir/cleaned_sample.csv"
df.to_csv(preprocessed_csv_file_path, index=False, quoting=1, encoding='utf-8')

# configurazione
config_path = "src/morph_kgc_changes_metadata_conversions/config.ini"
config = configparser.ConfigParser()
config.read(config_path)
config['DataSource1']['file_path'] = preprocessed_csv_file_path
with open(config_path, 'w') as config_file:
    config.write(config_file)

# materializzazione grafo
graph = materialize(config_path)

# file di output e il percorso di output
output_file = config['CONFIGURATION']['output_file']
output_dir = config['CONFIGURATION']['output_dir']
output_path = os.path.join(output_dir, output_file)

# grafo convertito in un oggetto rdflib.Graph se non lo è già
if not isinstance(graph, Graph):
    raise TypeError("Expected morph_kgc.materialize to return an rdflib.Graph object")

# mapping YARRRML in dizionario
yaml = YAML(typ='safe', pure=True)

with open('src/morph_kgc_changes_metadata_conversions/sample_mapping_file.yaml', 'r', encoding='utf-8') as file:
    yarrrml_data = yaml.load(file)

# estrazione prefissi e aggiunta a grafo
prefixes = yarrrml_data.get('prefixes', {})
for prefix, uri in prefixes.items():
    graph.bind(prefix, Namespace(uri))

# il grafo in Turtle, su file output
graph.serialize(destination=output_path, format='turtle')

# CORREZIONE (POSTPROCESSING)

# grafo per caricare rdf
g = Graph()
g.parse(output_path)

##  analisi tipi soggetto / oggetto
# for s, p, o in g:
#     # Determina il tipo del soggetto
#     if isinstance(s, URIRef):
#         print(f"Soggetto IRI: {s}")
#     elif isinstance(s, BNode):
#         print(f"Soggetto Blank Node: {s}")
#     elif isinstance(s, Literal):
#         print(f"Soggetto Literal: {s}")
#
# for s, p, o in g:
#     # Determina il tipo dell'oggetto
#     if isinstance(o, URIRef):
#         print(f"Oggetto IRI: {o}")
#     elif isinstance(o, BNode):
#         print(f"Oggetto Blank Node: {o}")
#     elif isinstance(o, Literal):
#         print(f"Oggetto Literal: {o}")



# lettura RDF come stringa
with open(output_path, 'r') as f:
    data = f.read()

# path del file di output
output_file_path = output_path.split(".")[0] + "_corretto.ttl"

# estrazione prefissi
def extract_prefixes(text):
    prfx = re.findall(r'@prefix\s([^\s:]+:)\s', text)
    return prfx

# regex generata sui prefissi
def generate_prefix_regex(prefixes):
    prefix_pattern = "|".join(re.escape(prefix) for prefix in prefixes)
    # pattern per match per ogni stringa tra virgolette che inizi per uno dei prefissi
    regex_pattern = rf'"({prefix_pattern})[^"]*"'
    return regex_pattern

# rimuovere le parentesi angolari da URI
def remove_angular_brackets(uri):
    return uri.strip('<>')# Funzione per rimuovere le parentesi angolari dalle URI

# rimuovere le parentesi angolari da URI
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

# rimuovere le virgolette da URI
def remove_apices(string):
    return string.strip('"')

# processare rdf in forma testuale
def process_rdf_data(data):
    prefixes = extract_prefixes(data)
    regex_pattern = generate_prefix_regex(prefixes)
    string_pattern = re.compile(regex_pattern)

    # matches = re.finditer(regex_pattern, data, re.MULTILINE)
    # matches_found = []
    # for matchNum, match in enumerate(matches, start=1):
    #     matches_found.append("{match}".format(matchNum=matchNum, start=match.start(), end=match.end(), match=match.group()))
    #     print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
    #                                                                         end=match.end(), match=match.group()))
    # print("matches_found", matches_found)

    # regex x trovare URI
    uri_pattern = re.compile(r'<(?!http|https)([^>]+)>')
    bad_form_uri_pattern = re.compile(r"(?:[\"]<?)(https?:\/\/[^\s\"'<>\]]+)(?:>[\"]|[\">?])")

    # sostituzione uri con parentesi angolari con uri senza
    def replace_uri(match):
        return remove_angular_brackets(match.group(0))

    # sostituzione uri tra virgolette con uri in parentesi angolari
    def replace_badform_uri(match):
        return remove_angular_apices_add_angular_brackets(match.group(0))

    # sostituzione uri con virgolette con uri senza
    def replace_str(match):
        return remove_apices(match.group(0))

    # regex per sostituire tutti URI
    processed_data = uri_pattern.sub(replace_uri, data)

    # regex per sostituire tutti URI
    processed_data = string_pattern.sub(replace_str, processed_data)

    # regex per sostituire URI badformed
    processed_data = bad_form_uri_pattern.sub(replace_badform_uri, processed_data)


    return processed_data

# esecuzione trasformazione
processed_data = process_rdf_data(data)

# stampa dati RDF trasformati
print(processed_data)

# scrittura su file di dati RDF trasformati
with open(output_file_path, 'w') as f:
    f.write(processed_data)