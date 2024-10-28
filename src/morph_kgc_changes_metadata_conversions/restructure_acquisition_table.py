import pandas as pd
import json
import copy
import re
import numpy as np
import pprint
from pprint import PrettyPrinter
from datetime import datetime, date
import re
import math

def rimuovi_sequenze_lettere(testo):
    # Pattern per una o più lettere (maiuscole o minuscole)
    pattern = r'[A-Za-z]+'
    # Sostituisci tutte le sequenze di lettere con uno spazio
    testo_modificato = re.sub(pattern, ' ', testo)
    # Rimuovi spazi multipli e spazi all'inizio/fine
    testo_pulito = re.sub(r'\s{2,}', ' ', testo_modificato).strip()
    return testo_pulito


def clean_value(value):
    if isinstance(value, str):
        value = value.strip()
        value = re.sub(r'[^\x00-\x7F]+', '', value)
        value = value.replace('"', "'")
    return value

def read_and_clean_csv(filepath):
    df = pd.read_csv(filepath, encoding='ISO-8859-1', header=[0,1,2])

    # Converti le colonne in un DataFrame per manipolarle
    col_df = df.columns.to_frame(index=False)

    # Sostituisci le etichette 'Unnamed' con NaN
    col_df.replace(to_replace=r'^Unnamed.*', value=np.nan, regex=True, inplace=True)

    # Riempie i valori NaN con il valore precedente lungo l'asse delle righe (axis=0)
    col_df.fillna(method='ffill', axis=0, inplace=True)

    # Combina i livelli delle colonne in un unico nome di colonna
    df.columns = [' - '.join([str(item).strip() for item in col if pd.notnull(item)]) for col in col_df.values]
    df.columns = make_unique(df.columns)
    return df
    # Rendi univoci i nomi delle colonne

def make_unique(column_names):
    seen = {}
    new_columns = []
    for col in column_names:
        if col in seen:
            seen[col] += 1
            new_columns.append(f"{col}.{seen[col]}")
        else:
            seen[col] = 0
            new_columns.append(col)
    return new_columns



def split_outside_parentheses(s, delimiter):
    result = []
    current = ''
    depth = 0  # Profondità delle parentesi
    for c in s:
        if c == '(':
            depth += 1
            current += c
        elif c == ')':
            depth -= 1
            current += c
        elif c == delimiter and depth == 0:
            result.append(current)
            current = ''
        else:
            current += c
    result.append(current)
    return result

def populate_dataset_json(dataset_structure, filepath):
    df = read_and_clean_csv(filepath)

    entities = []

    for index, row in df.iterrows():

        ent_dict_to_be_pop = copy.deepcopy(dataset_structure)

        row_dict = row.to_dict()
        pp = PrettyPrinter(indent=2, width=60, compact=True)
        pp.pprint(row_dict)

        for k, v in row_dict.items():
            if v and pd.notna(v):
                keyparts = [x.strip() for x in split_outside_parentheses(k, '-')]

                if len(keyparts) == 1:
                    if k in ent_dict_to_be_pop.keys():
                        ent_dict_to_be_pop[k] = v

                elif len(keyparts) == 2:
                    if keyparts[0] in ent_dict_to_be_pop.keys():
                        if keyparts[1] in ent_dict_to_be_pop[keyparts[0]]:
                            ent_dict_to_be_pop[keyparts[0]][keyparts[1]]= v

                elif len(keyparts) == 3:
                    if keyparts[0] in ent_dict_to_be_pop.keys():
                        if ent_dict_to_be_pop[keyparts[0]].get(keyparts[1]):
                            if keyparts[2] in ent_dict_to_be_pop[keyparts[0]][keyparts[1]]:
                                ent_dict_to_be_pop[keyparts[0]][keyparts[1]][keyparts[2]] = v

        entities.append(ent_dict_to_be_pop)

    # Salva le entità in un file JSON
    with open('output_acquisition_aldrovandi_cleaned.json', 'w', encoding='utf-8') as f:
        dizionario_finale = dict()
        iteratore_id = 0
        for entity in entities:
            if entity.get("NR"):
                id = clean_value(entity.get("NR"))
            else:
                id = "EXTID" + str(iteratore_id)
                iteratore_id += 1


            final_entity_cleaned = fix_process_date(entity, "acquisizione")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "processamento")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "modellazione")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "ottimizzazione")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "esportazione")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "metadatazione")
            final_entity_cleaned = fix_process_date(final_entity_cleaned, "caricamento")
            entity_cleaned = clean_entity(final_entity_cleaned)

            dizionario_finale[id] = entity_cleaned

        json.dump(dizionario_finale, f, ensure_ascii=False, indent=4)



def clean_entity(e):
    if isinstance(e, dict):
        return {k: clean_entity(v) for k, v in e.items()}
    elif isinstance(e, datetime):
        return e.isoformat()
    else:
        return clean_value(e)

def is_numeric_or_contains_digit(element):
    if isinstance(element, (int, float)):
        # Esclude i float NaN
        if isinstance(element, float) and math.isnan(element):
            return False
        return True
    elif isinstance(element, str):
        # Verifica se c'è almeno una cifra nella stringa
        return any(char.isdigit() for char in element)
    else:
        return False

def fix_process_date(entity, process_type):

    acquisition_correct_format_dates = {"Tempi di acquisizione": {
        "Data inizio (specificare data mm-dd)": "",
        "Data fine (specificare data mm-dd)": ""
    }}
    processamento_correct_format_dates = {"Tempi di processamento": {
        "Data inizio (specificare data mm-dd)": "",
        "Data fine (specificare data mm-dd)": ""
    }}
    modellazione_correct_format_dates = {"Tempi di modellazione": {
                "Data inizio (specificare data mm-dd)": "",
                "Data fine (specificare data mm-dd)": ""
            }}
    ottimizzazione_correct_format_dates = {"Tempi di ottimizzazione": {
                "Data inizio (specificare data mm-dd)": "",
                "Data fine (specificare data mm-dd)": ""
            }}
    esportazione_correct_format_dates = {"Tempi di esportazione": {
                "Data inizio (specificare data mm-dd)": "",
                "Data fine (specificare data mm-dd)": ""
            }}
    metadatazione_correct_format_dates = {"Tempi di metadatazione": {
                "Data inizio (specificare data mm-dd)": "",
                "Data fine (specificare data mm-dd)": ""
            }}

    caricamento_correct_format_dates = {"Tempi di caricamento": {
                "Data inizio (specificare data mm-dd)": "",
                "Data fine (specificare data mm-dd)": ""
            }}


    # ACQUISIZIONE

    if process_type == "acquisizione":
        acquisition_dates = entity["ACQUISIZIONE"]["Tempi di acquisizione"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not acquisition_dates or all(value is None for value in acquisition_dates.values()):
            entity["ACQUISIZIONE"]["Tempi di acquisizione"] = acquisition_correct_format_dates
            return entity

        all_acq_dates_in_v = [x for x in acquisition_dates.values() if x and len(x) > 1]
        all_acq_dates_in_k = [k for k,v in acquisition_dates.items() if v and len(v.strip())==1]
        all_acq_dates_ext_list = all_acq_dates_in_v + all_acq_dates_in_k
        all_acq_dates_ext_list_no_str_only = [x for x in all_acq_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_acq_dates_list_correct_format = [parse_date(x) for x in all_acq_dates_ext_list_no_str_only if parse_date(x)]

        if not all_acq_dates_list_correct_format:
            entity["ACQUISIZIONE"]["Tempi di acquisizione"] = acquisition_correct_format_dates
            return entity

        latest_date = str(max(all_acq_dates_list_correct_format))
        earliest_date = str(min(all_acq_dates_list_correct_format))

        acquisition_correct_format_dates["Tempi di acquisizione"]["Data inizio (specificare data mm-dd)"] = earliest_date
        acquisition_correct_format_dates["Tempi di acquisizione"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["ACQUISIZIONE"]["Tempi di acquisizione"] = acquisition_correct_format_dates

        return entity

    # PROCESSAMENTO

    if process_type == "processamento":
        processamento_dates = entity["PROCESSAMENTO"]["Tempi di processamento"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not processamento_dates or all(value is None for value in processamento_dates.values()):
            entity["PROCESSAMENTO"]["Tempi di processamento"] = processamento_correct_format_dates
            return entity

        all_proc_dates_in_v = [x for x in processamento_dates.values() if x and len(x) > 1]
        all_proc_dates_in_k = [k for k, v in processamento_dates.items() if v and len(v.strip()) == 1]
        all_proc_dates_ext_list = all_proc_dates_in_v + all_proc_dates_in_k
        all_proc_dates_ext_list_no_str_only = [x for x in all_proc_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_proc_dates_list_correct_format = [parse_date(x) for x in all_proc_dates_ext_list_no_str_only if parse_date(x)]

        if not all_proc_dates_list_correct_format:
            entity["PROCESSAMENTO"]["Tempi di processamento"] = processamento_correct_format_dates
            return entity

        latest_date = str(max(all_proc_dates_list_correct_format))
        earliest_date = str(min(all_proc_dates_list_correct_format))

        processamento_correct_format_dates["Tempi di processamento"][
            "Data inizio (specificare data mm-dd)"] = earliest_date
        processamento_correct_format_dates["Tempi di processamento"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["PROCESSAMENTO"]["Tempi di processamento"] = processamento_correct_format_dates

        return entity

    # MODELLAZIONE

    elif process_type == "modellazione":
        modellazione_dates = entity["MODELLAZIONE"]["Tempi di modellazione"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not modellazione_dates or all(value is None for value in modellazione_dates.values()):
            entity["MODELLAZIONE"]["Tempi di modellazione"] = modellazione_correct_format_dates
            return entity

        all_mod_dates_in_v = [x for x in modellazione_dates.values() if x and len(x) > 1]
        all_mod_dates_in_k = [k for k, v in modellazione_dates.items() if v and len(v.strip()) == 1]
        all_mod_dates_ext_list = all_mod_dates_in_v + all_mod_dates_in_k
        all_mod_dates_ext_list_no_str_only = [x for x in all_mod_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_mod_dates_list_correct_format = [parse_date(x) for x in all_mod_dates_ext_list_no_str_only if parse_date(x)]

        if not all_mod_dates_list_correct_format:
            entity["MODELLAZIONE"]["Tempi di modellazione"] = modellazione_correct_format_dates
            return entity

        latest_date = str(max(all_mod_dates_list_correct_format))
        earliest_date = str(min(all_mod_dates_list_correct_format))

        modellazione_correct_format_dates["Tempi di modellazione"][
            "Data inizio (specificare data mm-dd)"] = earliest_date
        modellazione_correct_format_dates["Tempi di modellazione"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["MODELLAZIONE"]["Tempi di modellazione"] = modellazione_correct_format_dates

        return entity

    # OTTIMIZZAZIONE

    elif process_type == "ottimizzazione":
        ottimizzazione_dates = entity["OTTIMIZZAZIONE"]["Tempi di ottimizzazione"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not ottimizzazione_dates or all(value is None for value in ottimizzazione_dates.values()):
            entity["OTTIMIZZAZIONE"]["Tempi di ottimizzazione"] = ottimizzazione_correct_format_dates
            return entity

        all_ott_dates_in_v = [x for x in ottimizzazione_dates.values() if x and len(x) > 1]
        all_ott_dates_in_k = [k for k, v in ottimizzazione_dates.items() if v and len(v.strip()) == 1]
        all_ott_dates_ext_list = all_ott_dates_in_v + all_ott_dates_in_k
        all_ott_dates_ext_list_no_str_only = [x for x in all_ott_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_ott_dates_list_correct_format = [parse_date(x) for x in all_ott_dates_ext_list_no_str_only if parse_date(x)]

        if not all_ott_dates_list_correct_format:
            entity["OTTIMIZZAZIONE"]["Tempi di ottimizzazione"] = ottimizzazione_correct_format_dates
            return entity

        latest_date = str(max(all_ott_dates_list_correct_format))
        earliest_date = str(min(all_ott_dates_list_correct_format))

        ottimizzazione_correct_format_dates["Tempi di ottimizzazione"][
            "Data inizio (specificare data mm-dd)"] = earliest_date
        ottimizzazione_correct_format_dates["Tempi di ottimizzazione"][
            "Data fine (specificare data mm-dd)"] = latest_date
        entity["OTTIMIZZAZIONE"]["Tempi di ottimizzazione"] = ottimizzazione_correct_format_dates

        return entity

    # ESPORTAZIONE

    elif process_type == "esportazione":
        esportazione_dates = entity["ESPORTAZIONE"]["Tempi di esportazione"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not esportazione_dates or all(value is None for value in esportazione_dates.values()):
            entity["ESPORTAZIONE"]["Tempi di esportazione"] = esportazione_correct_format_dates
            return entity

        all_exp_dates_in_v = [x for x in esportazione_dates.values() if x and len(x) > 1]
        all_exp_dates_in_k = [k for k, v in esportazione_dates.items() if v and len(v.strip()) == 1]
        all_exp_dates_ext_list = all_exp_dates_in_v + all_exp_dates_in_k
        all_exp_dates_ext_list_no_str_only = [x for x in all_exp_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_exp_dates_list_correct_format = [parse_date(x) for x in all_exp_dates_ext_list_no_str_only if parse_date(x)]

        if not all_exp_dates_list_correct_format:
            entity["ESPORTAZIONE"]["Tempi di esportazione"] = esportazione_correct_format_dates
            return entity

        latest_date = str(max(all_exp_dates_list_correct_format))
        earliest_date = str(min(all_exp_dates_list_correct_format))

        esportazione_correct_format_dates["Tempi di esportazione"][
            "Data inizio (specificare data mm-dd)"] = earliest_date
        esportazione_correct_format_dates["Tempi di esportazione"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["ESPORTAZIONE"]["Tempi di esportazione"] = esportazione_correct_format_dates

        return entity

    # METADATAZIONE

    elif process_type == "metadatazione":
        metadatazione_dates = entity["METADATAZIONE"]["Tempi di metadatazione"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not metadatazione_dates or all(value is None for value in metadatazione_dates.values()):
            entity["METADATAZIONE"]["Tempi di metadatazione"] = metadatazione_correct_format_dates
            return entity

        all_meta_dates_in_v = [x for x in metadatazione_dates.values() if x and len(x) > 1]
        all_meta_dates_in_k = [k for k, v in metadatazione_dates.items() if v and len(v.strip()) == 1]
        all_meta_dates_ext_list = all_meta_dates_in_v + all_meta_dates_in_k
        all_meta_dates_ext_list_no_str_only = [x for x in all_meta_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_meta_dates_list_correct_format = [parse_date(x) for x in all_meta_dates_ext_list_no_str_only if
                                              parse_date(x)]

        if not all_meta_dates_list_correct_format:
            entity["METADATAZIONE"]["Tempi di metadatazione"] = metadatazione_correct_format_dates
            return entity

        latest_date = str(max(all_meta_dates_list_correct_format))
        earliest_date = str(min(all_meta_dates_list_correct_format))

        metadatazione_correct_format_dates["Tempi di metadatazione"][
            "Data inizio (specificare data mm-dd)"] = earliest_date
        metadatazione_correct_format_dates["Tempi di metadatazione"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["METADATAZIONE"]["Tempi di metadatazione"] = metadatazione_correct_format_dates

        return entity

    # CARICAMENTO

    elif process_type == "caricamento":
        caricamento_dates = entity["CARICAMENTO SU ATON"]["Tempi di caricamento"]

        # NEL CASO IN CUI NON CI SIANO ULTERIORI DATI SULLE DATE DI INIZIO E DI FINE
        if not caricamento_dates or all(value is None for value in caricamento_dates.values()):
            entity["CARICAMENTO SU ATON"]["Tempi di caricamento"] = caricamento_correct_format_dates
            return entity

        all_car_dates_in_v = [x for x in caricamento_dates.values() if x and len(x) > 1]
        all_car_dates_in_k = [k for k, v in caricamento_dates.items() if v and len(v.strip()) == 1]
        all_car_dates_ext_list = all_car_dates_in_v + all_car_dates_in_k
        all_car_dates_ext_list_no_str_only = [x for x in all_car_dates_ext_list if is_numeric_or_contains_digit(x)]
        all_car_dates_list_correct_format = [parse_date(x) for x in all_car_dates_ext_list_no_str_only if parse_date(x)]

        if not all_car_dates_list_correct_format:
            entity["CARICAMENTO SU ATON"]["Tempi di caricamento"] = caricamento_correct_format_dates
            return entity

        latest_date = str(max(all_car_dates_list_correct_format))
        earliest_date = str(min(all_car_dates_list_correct_format))

        caricamento_correct_format_dates["Tempi di caricamento"]["Data inizio (specificare data mm-dd)"] = earliest_date
        caricamento_correct_format_dates["Tempi di caricamento"]["Data fine (specificare data mm-dd)"] = latest_date
        entity["CARICAMENTO SU ATON"]["Tempi di caricamento"] = caricamento_correct_format_dates

        return entity






# Funzione per il parsing delle date, inclusi i casi speciali
def parse_date(date_str):
    date_str = str(date_str).strip().lower()
    mon = ""
    months = {
        1: ["jan", "january", "gen", "gennaio"],
        2: ["feb", "february", "feb", "febbraio"],
        3: ["mar", "march", "mar", "marzo"],
        4: ["apr", "april", "apr", "aprile"],
        5: ["may", "maggio", "mag", "maggio"],
        6: ["jun", "june", "giu", "giugno"],
        7: ["jul", "july", "lug", "luglio"],
        8: ["aug", "august", "ago", "agosto"],
        9: ["sep", "september", "set", "settembre"],
        10: ["oct", "october", "ott", "ottobre"],
        11: ["nov", "november", "nov", "novembre"],
        12: ["dec", "december", "dic", "dicembre"]
    }
    for k, v in months.items():
        for m in v:
            if m in date_str:
                mon = k
                break

    date_list = []
    date_strip = date_str.strip(" ")
    if "-" in date_strip:
        date_list = date_strip.split("-")
    elif "." in date_strip:
        date_list = date_strip.split(".")
    elif "/" in date_strip:
        date_list = date_strip.split("/")
    elif "\\" in date_strip:
        date_list = date_strip.split("\\")
    else:
        date_list.append(date_strip)

    date_list_num = []
    if mon:
        if len(date_list) == 1:
            date_list_num.append("1")
            date_list_num.append(mon)
        elif len(date_list) == 2:
            date_list_num.append(date_list[0])
            date_list_num.append(mon)
        elif len(date_list) == 3:
            date_list_num.append(date_list[0])
            date_list_num.append(mon)
            date_list_num.append(date_list[2])
        else:
            raise ValueError("Check why there are more than 3 date parts in:", date_list)
    else:
        date_list_num = [x for x in date_list]

    date_converted = convert_to_date(date_list_num)

    return date_converted


def convert_to_date(input_date):
    """
    Converte una data fornita come lista o stringa in una stringa data standardizzata (YYYY-MM-DD).

    Formati supportati:
        - Lista: ['d', 'm', 'yy']
        - Stringa: 'd/m/yy', 'd.m.yy', 'd-m-yy'

    Args:
        input_date (list o str): La data da convertire.

    Returns:
        str: La data nel formato 'YYYY-MM-DD'.

    Raises:
        ValueError: Se il formato della data non è riconosciuto o è invalido.
    """
    if type(input_date) is datetime:
        input_date = input_date.strftime("%d-%m-%Y")
    elif type(input_date) is list:
        if len(input_date)<3:
            # Ottieni l'anno corrente
            anno_corrente = datetime.now().year

            # Calcola l'anno precedente
            anno_precedente = anno_corrente - 1

            # Converti l'anno precedente in formato a due cifre (YY)
            anno_precedente_yy = f"{anno_precedente % 100:02}"
            input_date.append(anno_precedente_yy)


    # Definisci i possibili separatori
    separatori = ['/', '.', '-']

    # Funzione per gestire la lista
    if isinstance(input_date, list):
        if len(input_date) != 3:
            if not input_date:
                return None
            raise ValueError("La lista deve contenere esattamente tre elementi: [giorno, mese, anno].")
        giorno, mese, anno = input_date
        # Converti in interi
        try:
            giorno = int(giorno)
            mese = int(mese)
            anno = int(anno)
        except ValueError:
            raise ValueError("Gli elementi della lista devono essere numerici.")

        # Gestisci anni a due cifre
        if anno < 100:
            anno += 2000  # Ad esempio, '23' diventa '2023'

        try:
            data_obj = date(anno, mese, giorno)
            return data_obj.strftime("%Y-%m-%d")
        except ValueError as ve:
            raise ValueError(f"Data non valida: {ve}")

    # Se è una stringa
    elif isinstance(input_date, str):
        # Identifica quale separatore viene usato
        pattern = '|'.join(map(re.escape, separatori))
        separatore_trovato = re.search(pattern, input_date)

        if separatore_trovato:
            sep = separatore_trovato.group()
        else:
            raise ValueError("Separatore non riconosciuto. Usa '/', '.', o '-'.")

        # Suddividi la stringa in parti
        parti = input_date.split(sep)

        if len(parti) != 3:
            raise ValueError("Formato data non valido. Usa 'd/m/yy', 'd.m.yy', o 'd-m-yy'.")

        giorno, mese, anno = parti
        parti_correct = []
        for x in parti:
            if x.startswith("0"):
                parti_correct.append(x[1:])
            else:
                parti_correct.append(x)


        # Converti in interi
        try:
            giorno = int(parti_correct[0])
            mese = int(parti_correct[1])
            anno = int(parti_correct[2])
        except ValueError:
            raise ValueError("I componenti della data devono essere numerici.")

        # Gestisci anni a due cifre
        if anno < 100:
            anno += 2000  # Ad esempio, '23' diventa '2023'

        try:
            data_obj = date(anno, mese, giorno)
            return data_obj.strftime("%Y-%m-%d")
        except ValueError as ve:
            raise ValueError(f"Data non valida: {ve}")

    else:
        raise TypeError("Il tipo di input deve essere una lista o una stringa.", type(input_date), input_date)


if __name__ == '__main__':
    filepath = 'src/morph_kgc_changes_metadata_conversions/dataset/dataset_acquisizione_aldrovandi/oggetti_mostra_chi_quando(STANZA 1).csv'

    # Struttura completa del dizionario acquisition_csv_structure
    acquisition_csv_structure = {
        "NR": None,
        "OGGETTO": None,
        "VETRINA": None,
        "DIDASCALIA": None,
        "STATO CORRENTE": None,
        "LINK MOD": None,
        "NOTE": None,
        "ACQUISIZIONE": {
            "Istituto responsabile acquisizione": None,
            "Persone responsabili acquisizione": None,
            "Tecnica di acquisizione": None,
            "Strumentazione di acquisizione": None,
            "Tempi di acquisizione": {
                "Aprile 23 o prima (specificare data mm-dd)": None,
                "17.04.23": None,
                "08.05.23": None,
                "15.05.23": None,
                "22.05.23": None,
                "29.05.23": None,
                "Giugno 23 o dopo (specificare data mm-dd)": None
            }
        },
        "PROCESSAMENTO": {
            "Istituto responsabile processamento": None,
            "Persone responsabili processamento": None,
            "Strumentazione di processamento": None,
            "Tempi di processamento": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        },
        "MODELLAZIONE": {
            "Istituto responsabile modellazione": None,
            "Persone responsabili modellazione": None,
            "Strumentazione di modellazione": None,
            "Tempi di modellazione": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        },
        "OTTIMIZZAZIONE": {
            "Istituto responsabile ottimizzazione": None,
            "Persone responsabili ottimizzazione": None,
            "Strumentazione di ottimizzazione": None,
            "Tempi di ottimizzazione": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        },
        "ESPORTAZIONE": {
            "Istituto responsabile esportazione": None,
            "Persone responsabili esportazione": None,
            "Strumentazione di esportazione": None,
            "Tempi di esportazione": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        },
        "METADATAZIONE": {
            "Istituto responsabile metadatazione": None,
            "Persone responsabili metadatazione": None,
            "Strumentazione di metadatazione": None,
            "Tempi di metadatazione": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        },
        "CARICAMENTO SU ATON": {
            "Istituto responsabile caricamento": None,
            "Persone responsabili caricamento": None,
            "Strumentazione di caricamento": None,
            "Tempi di caricamento": {
                "Data inizio (specificare data mm-dd)": None,
                "Data fine (specificare data mm-dd)": None
            }
        }
    }

    populate_dataset_json(acquisition_csv_structure, filepath)