import hpo2gene_parser
import os
import argparse

# save file in folder called source if not already existing
sourcedir = os.getcwd()
if os.path.isdir(sourcedir + "/" + "sources") is False:
    os.mkdir(sourcedir + "/" + "sources")

# Create HPO2gene annotation file
output_path = "./sources/hpo2genes.tsv"
hpo2gene_parser.hpo2gene_parser(output_path)

with open(output_path) as HPO2genes:
    gene_library = []
    for line in HPO2genes:
        tsplit = line.split("\t")
        gene_library.append([tsplit[0], str.replace(tsplit[1], "\n", "").strip("[]")])
HPO2genes.close()


def annotate_genes(input_path, out_path):
    """Main function:
    Args:
        input_path (str): Local path to the folder with HPO annotated clinical notes.
        out_path (str): Local path to folder where extracted genes for each clinical note should be stored.
    """
    notes = os.listdir(input_path)
    for lists in notes:
        if lists.endswith(".HPO.txt"):
            with open(input_path + "/" + lists) as file:
                patient = str.replace(file.read(), "\n", " ")
        file.close()

        patient_genes = []
        for term in gene_library[1:]:
            if term[0] in patient:
                patient_genes.append([term[0]+"\t", term[1].strip("[]").replace("'", "")])

        # print results in console
        print("Gene annotation done for %s.\n" % lists)

        # Output in txt file
        # create output folder if not already exists
        sourcedir = os.getcwd()
        if os.path.isdir(sourcedir + "/" + out_path) is False:
            os.mkdir(sourcedir + "/" + out_path)

        with open(out_path + "/" + lists.replace(".HPO.txt", ".genes.txt"), "w") as out:
            for item in patient_genes:
                item = str().join(item)
                out.write("%s\n\n" % item)
        out.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Map HPO genes to HPO annotated clin notes.")
    p.add_argument("-i", "--input_path", help="Local file path to the clinical notes with HPO.")
    p.add_argument("-o", "--output_path", help="Local path to folder to store the results.")
    args = p.parse_args()

    annotate_genes(
        args.input_path,
        args.output_path,
    )
