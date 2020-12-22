python myNLP2hpo_v2.py -i ./clinicalnotes -n -o ./v2_out_extracted_HPO

python annotate_genes.py -i ./v2_out_extracted_HPO -o ./v2_out_annotated_genes

python prioritize_genes.py -i ./v2_out_annotated_genes -o ./v2_out_prioritized_genes

python annotate_diseases.py -i ./v2_out_extracted_HPO -o ./v2_out_annotated_diseases

python prioritize_diseases.py -i ./v2_out_annotated_diseases -o ./v2_out_prioritized_diseases
