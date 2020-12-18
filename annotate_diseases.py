import hpo2disease_parser
import os
import argparse

# save file in folder called source if not already existing
sourcedir = os.getcwd()
if os.path.isdir(sourcedir + "/" + "sources") is False:
    os.mkdir(sourcedir + "/" + "sources")

# Create HPO2gene annotation file
output_path = "./sources/HPO2Diseases.tsv"
hpo2disease_parser.hpo2disease_parser(output_path)

with open(output_path) as HPO2diseases:
    disease_library = []
    for line in HPO2diseases:
        tsplit = line.split("\t")
        disease_library.append([tsplit[0], str.replace(tsplit[1], "\n", "")])
HPO2diseases.close()


def annotate_diseases(input_path, out_path):
    """Main function:
    Args:
        input_path (str): Local path to the folder with HPO annotated clinical notes.
        out_path (str): Local path to folder where extracted diseased for each clinical note should be stored.
    """
    notes = os.listdir(input_path)
    for lists in notes:
        if lists.endswith(".HPO.txt"):
            with open(input_path + "/" + lists) as file:
                patient = str.replace(file.read(), "\n", " ").replace("\t", " ")
        file.close()

        patient_diseases = []
        for term in disease_library[1:]:
            if term[0] in patient:
                patient_diseases.append([term[0]+"\t", term[1].strip("[]").replace("'", "")])

        # print results in console
        print("Disease annotation done for %s.\n" % lists)

        # Output in txt file
        # create output folder if not already exists
        sourcedir = os.getcwd()
        if os.path.isdir(sourcedir + "/" + out_path) is False:
            os.mkdir(sourcedir + "/" + out_path)

        with open(out_path + "/" + lists.replace(".HPO.txt", ".diseases.txt"), "w") as out:
            out.write("Patient_HPO_Id\tAnnotated_Diseases\n")
            for item in patient_diseases:
                item = str().join(item)
                out.write("%s\n\n" % item)
        out.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Map HPO disease to HPO annotated clin notes.")
    p.add_argument("-i", "--input_path", help="Local file path to the clinical notes with HPO.")
    p.add_argument("-o", "--output_path", help="Local path to folder to store the results.")
    args = p.parse_args()

    annotate_diseases(
        args.input_path,
        args.output_path,
    )
