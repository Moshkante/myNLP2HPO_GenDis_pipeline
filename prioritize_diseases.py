import os
import re
from collections import Counter
import argparse


def prioritize_diseases(input_path, output_path):
    """Main function:
    Args:
        input_path (str): Local path to the folder with HPO term and disease annotated clinical notes.
        output_path (str): Local path to folder where prioritized disease for each clinical note should be stored.
    """
    patients = os.listdir(input_path)
    for lists in patients:
        if lists.endswith(".diseases.txt"):
            with open(input_path + "/" + lists) as file:
                patient_diseases = str.replace(file.read(), "\t", " ")
        file.close()

        diseases_only = re.sub(r"(HP:).{7}", "", patient_diseases).replace("\n\n", "")
        diseases = re.findall(r"(?<=,)[^,]+(?=,)", diseases_only)
        disease_frequency = Counter(diseases).most_common()

        rank = 1
        ranked_diseases = []
        for word, frequency in disease_frequency:
            ranked_diseases.append([rank, word, frequency])
            rank = rank + 1

        # print results in console
        print("Disease prioritization by frequency done for %s.\n" % lists)

        # Output in txt file
        # create output folder if not already exists
        sourcedir = os.getcwd()
        if os.path.isdir(sourcedir + "/" + output_path) is False:
            os.mkdir(sourcedir + "/" + output_path)

        with open(output_path + "/" + lists.replace(".diseases.txt", ".prioritized_diseases.txt"), "w") as out:
            out.write("Rank\tDisease\tFrequency\n")
            for item in ranked_diseases:
                out.write("{}\t{}\t{}\n".format(item[0], item[1], item[2]))
        out.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Prioritize diseases from disease annotated clinical note.")
    p.add_argument("-i", "--input_path", help="Local file path to the clinical notes with annotated diseases.")
    p.add_argument("-o", "--output_path", help="Local path to folder to store the results.")
    args = p.parse_args()

    prioritize_diseases(
        args.input_path,
        args.output_path,
    )
