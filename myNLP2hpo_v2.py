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

output = "./sources/HPO_Terms.tsv"
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
synonyms_exp = []
synonyms_abbr = []
# exclude header from library
for line in library[1:]:
    if line[2].endswith("]"):
        # remove parenthesis and text within
        line[2] = (re.sub(r" \([^)]*\)", "", line[2]))
        # append only synonyms within double quote. Terms with abbreviated terms (or contain abbreviations)
        # are stored separately
        if "abbreviation" in line[2]:
            synonyms_abbr.append(re.findall('((?<=")[A-Z]+(?="))', line[2]))
            removed_abbr = re.sub('((?<=")\w+(?="))', '', line[2])
            synonyms_exp.append(re.findall('"(.*?)"', removed_abbr))
        else:
            synonyms_exp.append(re.findall('"(.*?)"', line[2]))
# remove empty synonym slots (resulted in '' due to replacement if abbreviation occurs)
synonyms_exp = [x for x in synonyms_exp if x != '']

# remove empty elements in list of lists where only a few synonyms disappear
# (exact abbreviations "synonyms_abbr" vs expressions containing abbreviation "synonyms")
synonyms_abbr = [x for x in synonyms_abbr if x != []]
synonyms = []
for syn in synonyms_exp:
    if '' in syn:
        synonyms.append(list(filter(None, syn)))
    else:
        synonyms.append(syn)

# split synonyms into single word, multiple word and abbreviated synonyms
singlesyn = []
multiplesyn = []
singlesyn_low = []
multiplesyn_low = []
morethanonesingsyn = []
morethanonesingsyn_low = []
morethanonemultsyn = []
morethanonemultsyn_low = []
abbreviatedsingsyn = []
abbreviatedmultsyn = []# no lower list in this case because we can only be sure if we look for uppercase abbreviation
# lower and capitalized lists for mapping (lower used to map the notes, capitalized used to find the related HPO term)

for syn in synonyms:
    if len(syn) > 1:
        for synn in syn:
            if ' ' in synn:
                morethanonemultsyn.append(synn)
                morethanonemultsyn_low.append(synn.lower())
            else:
                morethanonesingsyn.append(synn)
                morethanonesingsyn_low.append(synn.lower())
    else:
        for synn in syn:
            if ' ' in synn:
                multiplesyn.append(synn)
                multiplesyn_low.append(synn.lower())
            else:
                singlesyn.append(synn)
                singlesyn_low.append(synn.lower())

for syn in synonyms_abbr:
    if len(syn) > 1:
        for synn in syn:
            abbreviatedmultsyn.append(synn)
    else:
        abbreviatedsingsyn.append(syn)


# create function to stem the clinical note while keeping the order as well as for the multiple worded kw and syn
def stemTokens(tokens):
    stemmed_tokens=[]
    for tok in tokens:
        stemmed_tokens.append(PorterStemmer().stem(tok))
        stemmed_tokens.append(" ")
    return "".join(stemmed_tokens)


# Stemming aka lemmatization #######################################################################
# stem keywords and synonyms (take only stem of elements, 'model' and 'model'ing, no plural)
# We will check for lowered stemmed terms and lowered original terms, thus 2 dictionaries
# stem all synonym variants (except abbreviation, need to keep uppercase format)
stemmed_singlekw_low = set([PorterStemmer().stem(kw).lower() for kw in singlekw_low])
stemmed_multiplekw_low = set([PorterStemmer().stem(kw).lower() for kw in multiplekw_low])
stemmed_singlesyn_low = set([PorterStemmer().stem(syn).lower() for syn in singlesyn_low])
stemmed_multiplesyn_low = set([PorterStemmer().stem(syn).lower() for syn in multiplesyn_low])
stemmed_morethanonesingsyn_low = set([PorterStemmer().stem(syn).lower() for syn in morethanonesingsyn_low])
stemmed_morethanonemultsyn_low = set([PorterStemmer().stem(syn).lower() for syn in morethanonemultsyn_low])
# abbreviated synonyms are not stemmed, neither lowered
# Arrange dictionary to later mapping of extracted stemmed syn variants with the HPO via original synonyms
singlekw_dict_stem = {PorterStemmer().stem(kw).lower(): kw for kw in singlekw}
multiplekw_dict_stem = {PorterStemmer().stem(kw).lower(): kw for kw in multiplekw}
singlesyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in singlesyn}
multiplesyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in multiplesyn}
morethanonesingsyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in morethanonesingsyn}
morethanonemultsyn_dict_stem = {PorterStemmer().stem(syn).lower(): syn for syn in morethanonemultsyn}
# lower dictionary (without stem) because very few synonyms are cleared while stemmed (might be very small words)
singlekw_dict_low = {kw: kw.capitalize() for kw in singlekw_low}
multiplekw_dict_low = {kw: kw.capitalize() for kw in multiplekw_low}
singlesyn_dict_low = {kw: kw.capitalize() for kw in singlesyn_low}
multiplesyn_dict_low = {kw: kw.capitalize() for kw in multiplesyn_low}
morethanonesingsyn_dict_low = {syn: syn.capitalize() for syn in morethanonesingsyn_low}
morethanonemultsyn_dict_low = {syn: syn.capitalize() for syn in morethanonemultsyn_low}
#################################################################################################

# Preposition list to avoid the mapping of stemmed single-words that are similar to prepositions after stemming
# example: "intoe" becomes "into" after stemming, but is a synonym for a HPO term
prepositions = ["aboard", "about", "above", "across", "after", "against", "along", "amid", "among", "around",
                "as", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by",
                "concerning", "considering", "despite", "down", "during", "except", "following", "for", "from",
                "in", "inside", "into", "like", "minus", "near", "next", "of", "off", "on", "onto", "opposite",
                "out", "outside", "over", "past", "per", "plus", "regarding", "round", "save", "since", "than",
                "through", "till", "to", "toward", "under", "underneath", "unlike", "until", "up", "upon", "versus",
                "via", "with", "within", "without"]


def myNLP2hpo_v2(input_path, output_path, negation=False):
    """Main function:
    Args:
        input_path (str): Local path to the folder with clinical note texts. Title of the clinical text should
            refer to the patient, e.g. ID.
        output_path (str): Local path to folder where extracted HPO for each clinical note should be stored.
        negation (bool): Whether to add negation detection feature to the natural language processor.
    """

    # load in clinical notes one by one from the input_path
    clin_notes = os.listdir(input_path)
    table = str.maketrans(dict.fromkeys("()")) # to remove parenthesis from notes

    for clin in clin_notes:
        if clin.endswith('.txt'):
            with open(input_path + "/" + clin, encoding="UTF-8") as file:
                note = str.replace(file.read(), "\n", "")
                note = note.translate(table)
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
        # We will check for lowered stemmed terms and lowered original terms loaded before the function is called

        # stem tokens of note (only useful to map single keywords and single synonyms), keep order of text
        stemmed_tokens = stemTokens(tokens)
        #####################################################################################

        # now we have: single keywords, single synonyms, multiple-worded keywords, multiple-worded synonyms
        # and more than one synonym per term (which are also split into single and multiple-words)
        # and we have: notes tokens
        # all HP id, name and synonyms can be retrieved from the library

        # check if longer keywords, synonyms are in the clinical notes by matching substring
        HP_keywords_list = []
        HP_synonyms_list = []
        # saving the synonyms in the notes, first long versions, than single-worded, in both stemmed and lowered dicts
        for syn in stemmed_multiplesyn_low:
            if syn in note.lower():
                HP_synonyms_list.append(syn)

        for syn in multiplesyn_low:
            if PorterStemmer().stem(syn) in HP_synonyms_list:
                continue
            else:
                if syn in note.lower():
                    HP_synonyms_list.append(syn)

        for syn in stemmed_morethanonesingsyn_low:
            if syn in prepositions: # explanation above
                continue
            else:
                if syn in word_tokenize(stemmed_tokens.lower()):
                    HP_synonyms_list.append(syn)

        for syn in morethanonesingsyn_low:
            if PorterStemmer().stem(syn) in HP_synonyms_list:
                continue
            else:
                if syn in word_tokenize(note.lower()):
                    HP_synonyms_list.append(syn)

        for syn in stemmed_morethanonemultsyn_low:
            if syn in note.lower():
                HP_synonyms_list.append(syn)

        for syn in morethanonemultsyn_low:
            if PorterStemmer().stem(syn) in HP_synonyms_list:
                continue
            else:
                if syn in note.lower():
                    HP_synonyms_list.append(syn)

        for syn in synonyms_abbr:
            if syn in word_tokenize(note.upper()):
                HP_synonyms_list.append(syn)

        # saving the longer keywords in the notes
        for kw in stemmed_multiplekw_low:
            if kw in note.lower():
                HP_keywords_list.append(kw)

        for kw in multiplekw_low:
            if PorterStemmer().stem(kw) in HP_keywords_list:
                continue
            else:
                if kw in note.lower():
                    HP_keywords_list.append(kw)

        # check if single keywords and synonyms are in the clinical note by looking for exact match by token
        HP_keywords = set(stemmed_singlekw_low) & set(word_tokenize(stemmed_tokens.lower()))
        HP_keywords.update(set(singlekw_low) & set(word_tokenize(note.lower())))

        HP_synonyms = set(stemmed_singlesyn_low) & set(word_tokenize(stemmed_tokens.lower()))
        HP_synonyms.update(set(singlesyn_low) & set(word_tokenize(note.lower())))

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
                if u in singlekw_dict_low:
                    patient_kw.append(singlekw_dict_low[u])
                else:
                    if u in multiplekw_dict_stem:
                        patient_kw.append(multiplekw_dict_stem[u])
                    else:
                        if u in multiplekw_dict_low:
                            patient_kw.append(multiplekw_dict_low[u])
                        else:
                            print("The HPO keywords %s could not be remapped with the ontology." % u)

        for g in HP_synonyms_list:
            if g in HP_keywords_list:
                continue
            if g in singlesyn_dict_stem:
                patient_syn.append(singlesyn_dict_stem[g])
            else:
                if g in singlesyn_dict_low:
                    patient_syn.append(singlesyn_dict_low[g])
                else:
                    if g in multiplesyn_dict_stem:
                        patient_syn.append(multiplesyn_dict_stem[g])
                    else:
                        if g in multiplesyn_dict_low:
                            patient_syn.append(multiplesyn_dict_low[g])
                        else:
                            if g in morethanonesingsyn_dict_stem:
                                patient_syn.append(morethanonesingsyn_dict_stem[g])
                            else:
                                if g in morethanonesingsyn_dict_low:
                                    patient_syn.append(morethanonesingsyn_dict_low[g])
                                else:
                                    if g in morethanonemultsyn_dict_stem:
                                        patient_syn.append(morethanonemultsyn_dict_stem[g])
                                    else:
                                        if g in morethanonemultsyn_dict_low:
                                            patient_syn.append(morethanonemultsyn_dict_low[g])
                                        else:
                                            if g in synonyms_abbr:
                                                patient_syn.append(g)  # In case of abbreviations
                                            else:
                                                print("The HPO synonym %s could not be remapped with the ontology." % g)

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
            out.write("Patient_HPO_Id\tId_Name\n")
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

    myNLP2hpo_v2(
        args.input_path,
        args.output_path,
        negation=args.negation,
    )
