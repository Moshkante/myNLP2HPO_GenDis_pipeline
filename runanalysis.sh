python myNLP2hpo.py -i ./clinicalnotes -n -o ./out_extracted_HPO
python annotate_genes.py -i ./out_extracted_HPO -o ./out_annotated_genes
python prioritize_genes.py -i ./out_annotated_genes -o ./out_prioritized_genes
python annotate_diseases.py -i ./out_extracted_HPO -o ./out_annotated_diseases
python prioritize_diseases.py -i ./out_annotated_diseases -o ./out_prioritized_diseases