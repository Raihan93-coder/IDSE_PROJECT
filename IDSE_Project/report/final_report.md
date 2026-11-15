# ECG Arrhythmia Classification Results

## Dataset

{
  "rows": 87554,
  "columns": 188,
  "class_counts": {
    "0": 72471,
    "1": 2223,
    "2": 5788,
    "3": 641,
    "4": 6431
  },
  "missing_cells": 0,
  "duplicate_rows": 0
}

## Model

RandomForestClassifier, stratified five-fold randomized search optimizing macro F1.

## Results

- **accuracy:** 0.9769322126804312
- **precision_macro:** 0.9307067366553504
- **recall_macro:** 0.8502996961211402
- **f1_macro:** 0.8862014050018466
- **cv_best_macro_f1:** 0.7875173876279173
- **best_params:** {'model__n_estimators': 120, 'model__min_samples_split': 20, 'model__min_samples_leaf': 1, 'model__max_features': 'sqrt', 'model__max_depth': None, 'model__bootstrap': False}

## Classification report

```text
              precision    recall  f1-score   support

           0       0.98      1.00      0.99     18118
           1       0.91      0.67      0.77       556
           2       0.96      0.92      0.94      1448
           3       0.82      0.71      0.76       162
           4       0.99      0.95      0.97      1608

    accuracy                           0.98     21892
   macro avg       0.93      0.85      0.89     21892
weighted avg       0.98      0.98      0.98     21892
```
