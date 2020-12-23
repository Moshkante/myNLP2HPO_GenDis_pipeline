python myNLP2hpo_v3.py -i ./clinicalnotes -n -o ./v3_out_extracted_HPO

python annotate_genes.py -i ./v3_out_extracted_HPO -o ./v3_out_annotated_genes

python prioritize_genes.py -i ./v3_out_annotated_genes -o ./v3_out_prioritized_genes

python annotate_diseases.py -i ./v3_out_extracted_HPO -o ./v3_out_annotated_diseases

python prioritize_diseases.py -i ./v3_out_annotated_diseases -o ./v3_out_prioritized_diseases
