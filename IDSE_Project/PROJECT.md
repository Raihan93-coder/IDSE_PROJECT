# ECG Arrhythmia Classification using Random Forest

## Objective

Develop a complete end-to-end Data Science project that classifies ECG heartbeats into their corresponding classes using a Random Forest classifier.

The project should be suitable for an undergraduate Data Science course.

---

# Dataset

Use the best publicly available ECG heartbeat dataset.

Priority:

1. MIT-BIH Heartbeat Categorization Dataset (Kaggle)
2. MIT-BIH Arrhythmia Dataset
3. PhysioNet ECG Dataset

Automatically download the dataset.

Store inside

data/raw/

---

# Project Scope

The project must include

- Literature Survey
- Dataset Download
- Dataset Verification
- Exploratory Data Analysis
- Data Cleaning
- Feature Engineering
- Feature Selection
- Random Forest Model
- Hyperparameter Optimization
- Evaluation
- Final Testing
- Model Saving
- Report Generation
- PowerPoint Generation

---

# Exploratory Data Analysis

Generate

- Dataset overview
- Shape
- Class distribution
- Missing values
- Duplicate rows
- Correlation matrix
- Histograms
- Boxplots
- PCA visualization

Store plots inside

outputs/figures/

---

# Data Cleaning

Perform

- Missing value handling
- Duplicate removal
- Outlier detection
- Normalization if necessary
- Standardization if beneficial

Save cleaned dataset.

---

# Feature Engineering

Evaluate

- Variance Threshold
- Mutual Information
- Random Forest Feature Importance

Automatically choose the best features.

Generate feature importance plot.

---

# Model

Use ONLY

RandomForestClassifier

No other machine learning algorithm should be trained.

---

# Hyperparameter Optimization

Tune

- n_estimators
- max_depth
- min_samples_leaf
- min_samples_split
- max_features
- bootstrap

Use RandomizedSearchCV.

Use Stratified 5 Fold Cross Validation.

Optimize Macro F1 Score.

Stop when

- improvement <0.1% for 5 consecutive trials

OR

- 100 parameter combinations completed.

---

# Evaluation

Generate

Accuracy

Precision

Recall

Macro F1

Classification Report

Confusion Matrix

ROC Curve

Precision Recall Curve

Learning Curve

Feature Importance

---

# Save

Save

Model

Scaler

Feature Selector

Pipeline

using joblib.

---

# Report

Generate

Markdown

DOCX

PDF

---

# Presentation

Generate

12-slide PPTX

---

# Folder Structure

data/

outputs/

report/

src/

notebooks/

---

# Code Requirements

Modular

PEP8

Type Hints

Docstrings

Logging

Exception Handling

No duplicated code

---

# Final Deliverable

The project should run with

pip install -r requirements.txt

python src/train.py
