# ECG Arrhythmia Classification with Random Forest

Reproducible end-to-end classification of the public ECG Heartbeat Categorization dataset using **RandomForestClassifier only**.

## Run

```bash
pip install -r requirements.txt
python src/train.py
```

The script downloads the MIT-BIH heartbeat CSV files to `data/raw/`, checks and cleans them, runs EDA and feature selection, performs stratified five-fold RandomizedSearchCV (macro F1), evaluates a held-out test split, saves reusable joblib artifacts, and generates Markdown, DOCX, PDF and 12-slide PPTX reports. Network access is required on the first run. Existing raw CSVs are reused.

## Layout

- `data/raw/`: downloaded source CSVs
- `data/processed/`: cleaned train and test tables
- `outputs/figures/`: EDA and evaluation figures
- `outputs/models/`: fitted pipeline, selector and scaler
- `outputs/metrics/`: machine-readable results
- `report/`: literature survey, dataset notes and generated reports

The source dataset is [Kaggle ECG Heartbeat Categorization](https://www.kaggle.com/datasets/shayanfazeli/heartbeat); cite the dataset and original MIT-BIH Arrhythmia Database (Moody & Mark, 2001) in downstream work. Dataset redistribution terms remain those of the source.
