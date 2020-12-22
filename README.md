## Getting started
* Go to the myNLP2HPO_GenDis_pipeline directory.

* Replace test notes in the *clinicalnotes* folder with the desired clinical notes to analyze.

* Run the meta shell script `runanalysis.sh`. The pipeline requires a stable internet connection!

* Version 2 can be tested with the meta shell script `runanalysis_v2.sh`, which also requires internet connection. The folders created with the second version have the prefix "v2_".

## Definition of folders created while running the shell script

* `/sources`: contains three .tsv files, *HPO_Terms.tsv* with all HPO terms including synonyms and parent ids, *HPO2Genes.tsv* with genes linked to each HPO term and *HPO2Diseases.tsv* with diseases linked to each HPO term.
* `/out_extracted_HPO`: contains extracted HPO terms for each clinical note in the *clinicalnotes* folder as .txt files.
* `/out_annotated_genes`: contains annotated genes for every extracted HPO term from the clinical notes as .txt files.
* `/out_prioritized_genes`: contains genes prioritized and ranked by their frequency for each clinical note as .txt files.
* `/out_annotated_diseases`: contains annotated diseases for every extracted HPO term from the clinical notes as .txt files.
* `/out_prioritized_diseases`: contains diseases prioritized and ranked by their frequency for each clinical note as .txt files.
