import csv

def sample_csv(input_file, output_file, num_lines=3):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)

        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            # Read and write the first `num_lines` lines
            for i, row in enumerate(reader):
                if i < num_lines:
                    writer.writerow(row)
                else:
                    break


#  usage
input_csv = 'src/morph_kgc_changes_metadata_conversions/metadata_aldrovandi.csv'
output_csv = 'src/morph_kgc_changes_metadata_conversions/sample_input_file.csv'
sample_csv(input_csv, output_csv, num_lines=4)