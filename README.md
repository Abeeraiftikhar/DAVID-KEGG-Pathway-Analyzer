# KEGG Pathway Enrichment Dashboard

A Flask web application based on the supplied Google Colab workflow.

## Features

- Upload DAVID upregulated and downregulated CSV reports
- Automatically filter `KEGG_PATHWAY`
- Clean human KEGG identifiers such as `hsa04110:`
- Calculate `−log10(P-value)`
- Display pathway, gene count, P-value, Benjamini FDR and fold enrichment
- Generate:
  - `KEGG_Bar_Chart.png`
  - `KEGG_Bubble_Plot.png`
  - `KEGG_Combined_Figure.png`
  - `KEGG_All_Pathways_Summary.csv`
- 300 DPI PNG exports
- Responsive browser dashboard


## Expected DAVID columns

The uploaded CSV files should contain:

- Category
- Term
- Count
- P-Value
- Benjamini
- Fold Enrichment
- User Ids

Only rows where `Category == KEGG_PATHWAY` are analyzed.
