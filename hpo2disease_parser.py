import urllib
import urllib.request
import argparse


def hpo2disease_parser(output_path):
    url = "http://compbio.charite.de/jenkins/job/hpo.annotations.current/lastSuccessfulBuild/artifact/current/phenotype.hpoa"
    file = urllib.request.urlopen(url)
    hpo2disease_records_dict = {}
    current_diseases = []

    for line in file:
        decoded_line = line.decode("utf-8")
        if decoded_line.startswith("#"):  # to skip first line
            continue
        line_elements = decoded_line.rstrip().split('\t')
        tag = line_elements[3]
        value = line_elements[1]
        current_diseases.append([tag.strip("''"), value])

    for key, *value in current_diseases:
        hpo2disease_records_dict.setdefault(key, []).extend(value)

    with open(output_path, "wt") as path:
        for key, value in hpo2disease_records_dict.items():
            path.write("{}\t{}\n".format(key, list(dict.fromkeys(value))))
    path.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Map HPO terms to their diseases.")
    p.add_argument("-o", "--output_path", help="Local path to tsv file to store the results.")

    args = p.parse_args()

    hpo2disease_parser(
        args.output_path,
    )
