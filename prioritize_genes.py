import os
import re
from collections import Counter
import argparse


def prioritize_genes(input_path, output_path):
    """Main function:
    Args:
        input_path (str): Local path to the folder with HPO term and gene annotated clinical notes.
        output_path (str): Local path to folder where prioritized genes for each clinical note should be stored.
    """
    patients = os.listdir(input_path)
    for lists in patients:
        if lists.endswith(".genes.txt"):
            with open(input_path + "/" + lists) as file:
                patient_genes = str.replace(file.read(), "\t", " ")
        file.close()

        genes_only = re.sub(r"(HP:).{7}", "", patient_genes).replace("\n\n", "")
        genes = re.findall(r"\w+", genes_only)
        gene_frequency = Counter(genes).most_common()

        rank = 1
        ranked_genes = []
        for word, frequency in gene_frequency:
            ranked_genes.append([rank, word, frequency])
            rank = rank + 1

        # print results in console
        print("Gene prioritization by frequency done for %s.\n" % lists)

        # Output in txt file
        # create output folder if not already exists
        sourcedir = os.getcwd()
        if os.path.isdir(sourcedir + "/" + output_path) is False:
            os.mkdir(sourcedir + "/" + output_path)

        with open(output_path + "/" + lists.replace(".genes.txt", ".prioritized_genes.txt"), "w") as out:
            out.write("Rank\tGene\tFrequency\n")
            for item in ranked_genes:
                out.write("{}\t{}\t{}\n".format(item[0], item[1], item[2]))
        out.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Prioritize genes from gene annotated clinical note.")
    p.add_argument("-i", "--input_path", help="Local file path to the clinical notes with annotated genes.")
    p.add_argument("-o", "--output_path", help="Local path to folder to store the results.")
    args = p.parse_args()

    prioritize_genes(
        args.input_path,
        args.output_path,
    )
