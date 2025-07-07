# CHANGES Metadata Conversion Plugin

## Sponsor :shield:

<p align="center">
<img src="https://github.com/morph-kgc/morph-kgc-docs/blob/main/docs/assets/BASF.png" height="100" alt="BASF">
</p>

## To Do:
- produce mapping for acquisition process 
- Manage both VIAF and ULAN in case a different id is found 
- Issue with angular brackets, quotes, and datatype managed in pre or post processing. To be authomatized with mapping. See also: Issue with specifying types (IRI/string/etc) when using a function. Check if it's manageable also with YARRRML (it is possible with a RML mapping, try using the official converter). For now: default post-processing is executed on the first version of the RDF file just produced.
- Similarly, the `clean_csv` is necessary for extracting the language – Verify with the suggestion by the developer.
- Clarify licenses and IRI of licenses. 
- Consider uniforming name-surname order.
- Keep for now a unique file for all the triples, consider separating for each entity. 
- Make the code command-line-executable.
- Implementing the possibility of splitting the files production (one for each ATON object, for example).
- Flask webserver for easily exploitable UI.
- *Fonte*, *Immagine digitale*, *Iconografia* non sono attualmente modellate.

---

## How to run the code

### Preprocessing
```bash
python src/morph_kgc_changes_metadata_conversions/clean_csv.py
```
- Change manually the paths of the input and the output file (where the input file is the raw one and the output file is the postprocessed input. In the current execution, the file is overwritten).

### Triples production and postprocessing
```bash
python main_aldrovandi.py
```
- Change manually input, output, mapping and configuration paths if needed.
- The execution of this file postprocesses the produced data and fixes issues related to the datatypes of the subjects and objects of the produced triples, where needed.

### Current mapping file path 
```
src/morph_kgc_changes_metadata_conversions/sample_mapping_file.yaml
```

### Structure of the input file
- The code currently accepts as input CSV tables structured as in the sample at:

```
src/morph_kgc_changes_metadata_conversions/sample_input_3_entries.csv
```

---

## Understanding and Running the Scripts – CHANGES

### Premises

To execute the conversion process from CSV to RDF serialization, the Morph-KGC code (https://morph-kgc.readthedocs.io/en/stable/) has been extended. Morph-KGC is software based on the use of RDF Mapping Language (RML, https://rml.io/specs/rml/) conversion technology. Below, the main components are described to understand their structure and usage.

### Objectives

Interaction with the software extension is minimal and aimed at producing data in Turtle RDF serialization. This allows leveraging the semantic potential of the information internally connected and with external resources.

### Operational Actions

A general overview of the software components and the possible user interactions is provided below. However, for more detailed information on using the software to produce data in Turtle RDF format, please refer to the `README.md` file, which will be updated alongside the code.

#### Mapping Files – Definition of Conversion Rules

These consist of two YARRRML mapping files (https://rml.io/yarrrml/), one for each of the input datasets and modules of the Application Profile (objects and acquisition). These files define the rules for converting data into RDF format based on the project’s Application Profile. Users do not interact with these files as they are precompiled to cover all scenarios presented in datasets formulated according to the previously described guidelines.

#### Configuration File – Configuration of Conversion Parameters

This is an `.ini` file where the values of parameters concerning general configurations and each input dataset are defined. For compiling the configuration file, refer to the aforementioned `README.md` file.

In the section concerning the configuration of general parameters (`[CONFIGURATION]`), both mandatory and optional, the user defines:
- `output_file`: the name of the output file,
- `output_format`: the format (e.g., Turtle, N-Triples),
- `output_dir`: the directory where the file will be saved.

For input datasets, multiple sources can be configured using distinct sections like `[DataSource1]`, `[DataSource2]`, each pointing to its specific CSV file and mapping file.

```ini
[CONFIGURATION]
na_values = ,#N/A,N/A,#N/A N/A,n/a,NA,<NA>,#NA,NULL,null,nan,None
output_file = knowledge-graph.ttl
output_dir = src/morph_kgc_changes_metadata_conversions/output_dir
output_format = N-TRIPLES
only_printable_characters = no
safe_percent_encoding =
mapping_partitioning = PARTIAL-AGGREGATIONS
infer_sql_datatypes = no
logging_level = INFO
logs_file =
oracle_client_lib_dir =
oracle_client_config_dir =

[DataSource1]
mappings = src/morph_kgc_changes_metadata_conversions/sample_mapping_file.yaml
mapping_format = YARRRML
file_path = src/morph_kgc_changes_metadata_conversions/metadata_aldrovandi.csv
delimiter = ,
quotechar = "
encoding = utf-8
```

---

### User-Defined Functions – Handling Specific Cases and Interpreting Complex Data

These are declarative transformation functions implemented through the RML-FNML (RML Function Mapping Language). RML already provides a set of built-in functions, such as extracting multiple values within the same cell. Additional case-study-specific functions (e.g., technique normalization via AAT codes) are included. In general, the user does **not need** to modify these unless new, unanticipated values are introduced.

### Launch Script – Executing the Conversion

The launch script also handles:
- Preprocessing (e.g., cleaning and normalizing the CSV),
- Postprocessing (e.g., fixing malformed RDF elements),
- Executing the full CSV-to-RDF pipeline.

Command to run the full conversion:

```bash
python convert_to_rdf.py -obj <csv_input_file_objects> -acq <csv_input_file_acquisition>
```

---

### Summary of Sections

1. **Premises**: Introduction to the software and its purpose  
2. **Objectives**: Goals of using the software extension  
3. **Operational Actions**: Overview of software components and user interactions  
   - Mapping Files  
   - Configuration File  
   - User-Defined Functions  
   - Launch Script  

---

### Additional Notes

- **Mapping Files**: Ensure the YARRRML mapping files are correctly formatted and aligned with each dataset.  
- **Configuration Parameters**: Set `output_file`, `output_format`, and `output_dir` to match your needs.  
- **User-Defined Functions**: Customize only if new cases arise.  
- **Launch Scripts**: Check that all dependencies and paths are correctly set.

---

### References

The software is based on Morph-KGC, as documented in:

**[SoftwareX](https://www.sciencedirect.com/science/article/pii/S2352711024000803)** and  
**[SWJ](https://www.doi.org/10.3233/SW-223135)**

```bib
@article{arenas2024rmlfnml,
  title = {{An RML-FNML module for Python user-defined functions in Morph-KGC}},
  author = {Julián Arenas-Guerrero and Paola Espinoza-Arias and José Antonio Bernabé-Diaz and Prashant Deshmukh and José Luis Sánchez-Fernández and Oscar Corcho},
  journal = {SoftwareX},
  year = {2024},
  volume = {26},
  pages = {101709},
  issn = {2352-7110},
  publisher = {Elsevier},
  doi = {10.1016/j.softx.2024.101709}
}
@article{arenas2024morph,
  title     = {{Morph-KGC: Scalable knowledge graph materialization with mapping partitions}},
  author    = {Arenas-Guerrero, Julián and Chaves-Fraga, David and Toledo, Jhon and Pérez, María S. and Corcho, Oscar},
  journal   = {Semantic Web},
  year      = {2024},
  volume    = {15},
  number    = {1},
  pages     = {1-20},
  issn      = {2210-4968},
  publisher = {IOS Press},
  doi       = {10.3233/SW-223135}
}
```
