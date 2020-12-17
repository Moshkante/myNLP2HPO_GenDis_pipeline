"""
This function takes in file path of clinical notes and outputs HPO terms that are successfully
mapped to the clinical note text. Unlike the common state-of-the-art, this NLP is not relying on the
Unified Medical Language System (UMLS) and therefore does not require a third-party license. Might still
subject to changes while benchmarking.
"""

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import obo_parser
import itertools
import re
import os
import argparse

# Create recent HPO library of HPO terms only related to phenotypic abnormalities (HP:0000118)
# The parsed HPO library will be saved in the current directory and is used by the function.
hpo_url = "http://purl.obolibrary.org/obo/hp.obo"

# save file in folder called source if not already existing
sourcedir = os.getcwd()
if os.path.isdir(sourcedir + "/" + "sources") is False:
    os.mkdir(sourcedir + "/" + "sources")

output = "./sources/HPO.tsv"
phenotypic_abnormalities = "HP:0000118"
children_category = True
obo_parser.convert_obo_to_tsv(hpo_url, output, phenotypic_abnormalities, children_category)

with open(output) as HPO:
    library = []
    for line in HPO:
        tsplit = line.split("\t")
        library.append([tsplit[0], tsplit[1], tsplit[9]])
HPO.close()

# extract HPO term names to keywords
keywords = []
# exclude header from library
for row in library[1:]:
    keywords.append(row[1])

# split keywords into single and multiple keywords
singlekw = []
multiplekw = []
singlekw_low = []
multiplekw_low = []
for term in keywords:
    if ' ' in term:
        multiplekw.append(term)
        multiplekw_low.append(term.lower())
    else:
        singlekw.append(term)
        singlekw_low.append(term.lower())

# get synonym strings
synonyms = []
# exclude header from library
for line in library[1:]:
    if line[2].endswith("]"):
        # remove parenthesis and text within
        line[2] = (re.sub(r" \([^)]*\)", "", line[2]))
        # append only synonyms within double quote
        synonyms.append(re.findall('"(.*?)"', line[2]))

# split synonyms into single word and multiple word synonyms
singlesyn = []
multiplesyn = []
singlesyn_low = []
multiplesyn_low = []
morethanonesyn = []
morethanonesyn_low = []
for syn in synonyms:
    if len(syn) > 1:
        for synn in syn:
            morethanonesyn.append(synn)
            morethanonesyn_low.append(synn.lower())
    else:
        for synn in syn:
            if ' ' in synn:
                multiplesyn.append(synn)
                multiplesyn_low.append(synn.lower())
            else:
                singlesyn.append(synn)
                singlesyn_low.append(synn.lower())


def myNLP2hpo(input_path, output_path, negation=False):
    """Main function:
    Args:
        input_path (str): Local path to the folder with clinical note texts. Title of the clinical text should
            refer to the patient, e.g. ID.
        output_path (str): Local path to folder where extracted HPO for each clinical note should be stored.
        negation (bool): Whether to add negation detection feature to the natural language processor.
    """

    # load in clinical notes one by one from the input_path
    clin_notes = os.listdir(input_path)
    for clin in clin_notes:
        if clin.endswith('.txt'):
            with open(input_path + "/" + clin, encoding="UTF-8") as file:
                note = str.replace(file.read(), "\n", "")
        else:
            print("There is no text file in the given directory.")
            break
        file.close()

        # tokenize text (split each word and assign it as token for easier processing)
        tokens = word_tokenize(note)

        if negation is True:
            # tag terms that follow negations with the prefix "Not_" until the next punctuation mark
            NEGATION_ADVERBS = ["no", "without", "nil", "not", "n't", "never", "none", "neither", "nor", "non"]
            punctuations = [",", ".", ";", ":", "!", "?", "(", ")", "[", "]", "{", "}", "/"]

            for num, tok in enumerate(tokens, start=0):
                if tok.lower() in NEGATION_ADVERBS:
                    while tokens[num+1] not in punctuations:
                        tokens[num+1] = "Not_"+tokens[num+1]
                        num = num+1

            # in case a sentence starts with negation adverbs, the entire sentence is negated
            for num, tok in enumerate(tokens, start=0):
                if tok.lower() in NEGATION_ADVERBS and tokens[num-1] == ".":
                    while tokens[num+1] != ".":
                        tokens[num+1] = "Not_"+tokens[num+1]
                        num = num+1

            note = " ".join(tokens)

        # Stemming #######################################################################
        # stem the tokens, keywords and synonyms (take only stem of elements, 'model' and 'model'ing, no plural)
        stemmed_tokens = set([PorterStemmer().stem(tok).lower() for tok in tokens])

        stemmed_singlekw_low = set([PorterStemmer().stem(kw).lower() for kw in singlekw_low])
        stemmed_multiplekw_low = set([PorterStemmer().stem(kw).lower() for kw in multiplekw_low])
        stemmed_singlesyn_low = set([PorterStemmer().stem(syn).lower() for syn in singlesyn_low])
        stemmed_multiplesyn_low = set([PorterStemmer().stem(syn).lower() for syn in multiplesyn_low])
        stemmed_morethanonesyn_low = set([PorterStemmer().stem(syn).lower() for syn in morethanonesyn_low])

        singlekw_dict_stem = {PorterStemmer().stem(kw).lower(): kw for kw in singlekw}
        multiplekw_dict_stem = {PorterStemmer().stem(kw).lower(): kw for kw in multiplekw}
        singlesyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in singlesyn}
        multiplesyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in multiplesyn}
        morethanonesyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in morethanonesyn}

        # lower dictionary for multiple ones
        multiplekw_dict_low = {kw: kw.capitalize() for kw in multiplekw_low}
        multiplesyn_dict_low = {kw: kw.capitalize() for kw in multiplesyn_low}
        morethanonesyn_dict_low = {syn: syn.capitalize() for syn in morethanonesyn_low}
        #####################################################################################
        #####################################################################################

        # now we have: single keywords, single synonyms, multiple-worded keywords, multiple-worded synonyms
        # and more than one synonym per term
        # and we have: notes tokens
        # all HP id, name and synonyms can be retrieved from the library

        # check if longer keywords, synonyms are in the clinical notes by matching substring
        HP_keywords_list = []
        HP_synonyms_list = []

        # saving the synonyms in the notes
        for syn in stemmed_multiplesyn_low:
            if syn in note.lower():
                HP_synonyms_list.append(syn)

        for syn in multiplesyn_low:
            if syn in HP_synonyms_list:
                continue
            else:
                if syn in note.lower():
                    HP_synonyms_list.append(syn)

        for syn in morethanonesyn_low:
            if syn in HP_synonyms_list:
                continue
            else:
                if syn in note.lower():
                    HP_synonyms_list.append(syn)

        for syn in stemmed_morethanonesyn_low:
            if syn in HP_synonyms_list:
                continue
            else:
                if syn in note.lower():
                    HP_synonyms_list.append(syn)

        # saving the longer keywords in the notes
        for kw in multiplekw_low:
            if kw in note.lower():
                HP_keywords_list.append(kw)

        for kw in stemmed_multiplekw_low:
            if kw in HP_keywords_list:
                continue
            else:
                if kw in note.lower():
                    HP_keywords_list.append(kw)

        # check if single keywords and synonyms are in the clinical note by looking for exact match by token
        HP_keywords = set(stemmed_singlekw_low) & set(stemmed_tokens)
        HP_synonyms = set(stemmed_singlesyn_low) & set(stemmed_tokens)

        # Gather all information together in a list
        HP_keywords_list += list(HP_keywords)
        HP_synonyms_list += list(HP_synonyms)

        # Collect HP_id information for every matched synonym and term
        patient_kw = []
        patient_syn = []
        for u in HP_keywords_list:
            if u in singlekw_dict_stem:
                patient_kw.append(singlekw_dict_stem[u])
            else:
                if u in multiplekw_dict_stem:
                    patient_kw.append(multiplekw_dict_stem[u])
                else:
                    if u in multiplekw_dict_low:
                        patient_kw.append(multiplekw_dict_low[u])
                    else:
                        print("The HPO keywords %s could not be found in the clinical note." % u)

        for g in HP_synonyms_list:
            if g in HP_keywords_list:
                continue

            if g in singlesyn_dict_stem:
                patient_syn.append(singlesyn_dict_stem[g])
            else:
                if g in multiplesyn_dict_stem:
                    patient_syn.append(multiplesyn_dict_stem[g])
                else:
                    if g in multiplesyn_dict_low:
                        patient_syn.append(multiplesyn_dict_low[g])
                    else:
                        if g in morethanonesyn_dict_low:
                            patient_syn.append(morethanonesyn_dict_low[g])
                        else:
                            if g in morethanonesyn_dict_stem:
                                patient_syn.append(morethanonesyn_dict_stem[g])
                            else:
                                print("The HPO synonym %s could not be found in the clinical notes." % g)

        # now we have the patient variable filled with HPO keywords or synonyms that fit to HPO terms in the library
        patient_HPO = []
        for row in patient_kw:
            # exclude library header
            for line in library[1:]:
                if row == line[1]:
                    patient_HPO.append([line[0], line[1]])

        for row in patient_syn:
            # exclude library header
            for line in library[1:]:
                if row in re.findall('"(.*?)"', line[2]):
                    patient_HPO.append([line[0], line[1]])

        # remove duplicated patient HPO terms
        patient_HPO.sort()
        patient_HPO_final = list(patient_HPO for patient_HPO, _ in itertools.groupby(patient_HPO))

        # print results in console
        print("\n", patient_HPO_final, "\n\n in total %s HPO terms successfully extracted from the clinical note %s."
              % (len(patient_HPO_final), clin))

        # Output in txt file
        # create output folder if not already exists
        sourcedir = os.getcwd()
        if os.path.isdir(sourcedir + "/" + output_path) is False:
            os.mkdir(sourcedir + "/" + output_path)

        # setup regex compiler to put a white space between HPO_id and HPO_term
        rx = re.compile(r'(?<=\d)(?=[^\d\s])')

        with open(output_path + "/" + clin.replace(".txt", ".HPO.txt"), "w") as out:
            out.write("patient_HPO_id\tid_name\n")
            for item in patient_HPO_final:
                item = str().join(item)
                it = rx.sub('\t', item)
                out.write("%s\n" % it)
        out.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Map HPO terms to clinical note.")
    p.add_argument("-i", "--input_path", help="Local file path to the clinical notes.")
    p.add_argument("-o", "--output_path", help="Local path to folder to store the results.")
    p.add_argument("-n", "--negation", action="store_true", help="Whether negation should be considered."
                                                                 "To enable negation put -n.")
    args = p.parse_args()

    myNLP2hpo(
        args.input_path,
        args.output_path,
        negation=args.negation,
    )
