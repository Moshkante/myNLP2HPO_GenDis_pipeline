#1: Go to the myNLP2hpogenes_pipeline directory.

#2: Create a folder named "clinicalnotes" in this directory with all the clinical notes.

#3: Run the meta shell script 'runanalysis.sh'.


Definition of folders created while running the shell script:

sources: contains two .tsv files, "HPO.tsv" with all HPO terms and "hpo2genes.tsv" with genes linked to each HPO term.
out_extracted_HPO: contains extracted HPO terms for each clinical note in the "clinicalnotes" folder as .txt files.
out_annotated_genes: contains annotated genes for every extracted HPO term from the clinical notes as .txt files.
out_prioritized_genes: contains genes prioritized and ranked by their frequency for each clinical note as .txt files.
