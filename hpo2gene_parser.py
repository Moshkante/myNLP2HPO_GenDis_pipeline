import urllib
import urllib.request
import argparse


def hpo2gene_parser(output_path):
    url = "http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/util/annotation/phenotype_to_genes.txt"
    file = urllib.request.urlopen(url)
    hpo2gene_records_dict = {}
    current_genes = []

    for line in file:
        decoded_line = line.decode("utf-8")
        if decoded_line.startswith("#"):  # to skip first line
            continue
        line_elements = decoded_line.rstrip().split('\t')
        tag = line_elements[0]
        value = line_elements[3]
        current_genes.append([tag.strip("''"), value])

    for key, *value in current_genes:
        hpo2gene_records_dict.setdefault(key, []).extend(value)

    with open(output_path, "wt") as path:
        for key, value in hpo2gene_records_dict.items():
            path.write("{}\t{}\n".format(key, value))
    path.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Map HPO terms to their genes.")
    p.add_argument("-o", "--output_path", help="Local path to tsv file to store the results.")

    args = p.parse_args()

    hpo2gene_parser(
        args.output_path,
    )
