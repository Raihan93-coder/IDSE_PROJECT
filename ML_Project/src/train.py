"""End-to-end ECG heartbeat classification.

Inputs: public Kaggle MIT-BIH heartbeat CSVs, downloaded on demand.
Outputs: cleaned data, EDA figures, RF artifacts, metrics, and reports.
Usage: ``python src/train.py`` after installing requirements.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import Any

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.transformers import FixedFeatureSelector
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, VarianceThreshold, mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             ConfusionMatrixDisplay, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_curve, auc,
                             average_precision_score)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, learning_curve, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, label_binarize

RAW = ROOT / "data/raw"
PROC = ROOT / "data/processed"
FIG = ROOT / "outputs/figures"
MODELS = ROOT / "outputs/models"
METRICS = ROOT / "outputs/metrics"
REPORT = ROOT / "report"
SEED = 42
LOG = logging.getLogger("ecg")


def setup() -> None:
    """Create output folders and configure persistent logging."""
    for path in (RAW, PROC, FIG, MODELS, METRICS, REPORT):
        path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(ROOT / "outputs/run.log", encoding="utf-8"), logging.StreamHandler()])


def download_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Download and validate source train/test CSVs; return dataframes."""
    urls = {"mitbih_train.csv", "mitbih_test.csv"}
    if not all((RAW / name).exists() and (RAW / name).stat().st_size > 1000 for name in urls):
        LOG.info("Downloading public Kaggle heartbeat dataset")
        archive = RAW / "heartbeat.zip"
        try:
            response = requests.get("https://www.kaggle.com/api/v1/datasets/download/shayanfazeli/heartbeat", timeout=300)
            response.raise_for_status()
            archive.write_bytes(response.content)
            if not zipfile.is_zipfile(archive):
                raise ValueError("Kaggle returned a non-ZIP response")
            with zipfile.ZipFile(archive) as zf:
                for name in urls:
                    matches = [member for member in zf.namelist() if Path(member).name == name]
                    if not matches:
                        raise ValueError(f"Dataset archive is missing {name}")
                    (RAW / name).write_bytes(zf.read(matches[0]))
            archive.unlink(missing_ok=True)
        except Exception as exc:
            archive.unlink(missing_ok=True)
            raise RuntimeError(f"Could not download Kaggle dataset; check network access: {exc}") from exc
    frames = [pd.read_csv(RAW / n, header=None) for n in ("mitbih_train.csv", "mitbih_test.csv")]
    if any(df.shape[1] != 188 or df.empty for df in frames):
        raise ValueError("Invalid dataset: expected nonempty CSVs with 187 signal columns and one label.")
    for frame in frames:
        labels = pd.to_numeric(frame.iloc[:, -1], errors="coerce")
        if labels.isna().any() or not set(labels.unique()).issubset({0, 1, 2, 3, 4}):
            raise ValueError("Invalid dataset: labels must be numeric MIT-BIH classes 0 through 4.")
    return frames[0], frames[1]


def save_eda(train: pd.DataFrame) -> dict[str, Any]:
    """Write dataset overview and required exploratory figures."""
    x, y = train.iloc[:, :-1], train.iloc[:, -1].astype(int)
    summary = {"rows": int(len(train)), "columns": int(train.shape[1]), "class_counts": y.value_counts().sort_index().to_dict(),
               "missing_cells": int(train.isna().sum().sum()), "duplicate_rows": int(train.duplicated().sum())}
    q1, q3 = x.quantile(.25), x.quantile(.75)
    outlier_cells = x.lt(q1 - 1.5 * (q3 - q1), axis="columns") | x.gt(q3 + 1.5 * (q3 - q1), axis="columns")
    summary["iqr_outlier_cells"] = int(outlier_cells.sum().sum())
    (REPORT / "dataset_summary.md").write_text("# Dataset summary\n\n" + "\n".join(f"- **{k}:** {v}" for k, v in summary.items()), encoding="utf-8")
    y.value_counts().sort_index().plot(kind="bar", title="Heartbeat class distribution"); plt.xlabel("Class"); plt.ylabel("Rows"); plt.tight_layout(); plt.savefig(FIG / "class_distribution.png"); plt.close()
    x.iloc[:, :12].hist(figsize=(12, 8), bins=30); plt.tight_layout(); plt.savefig(FIG / "histograms.png"); plt.close()
    x.iloc[:, :12].plot(kind="box", figsize=(12, 5), showfliers=False); plt.tight_layout(); plt.savefig(FIG / "boxplots.png"); plt.close()
    plt.figure(figsize=(12, 9)); plt.imshow(x.corr(), cmap="coolwarm", vmin=-1, vmax=1, aspect="auto"); plt.colorbar(); plt.title("Feature correlation matrix"); plt.tight_layout(); plt.savefig(FIG / "correlation_matrix.png"); plt.close()
    sample = x.sample(min(6000, len(x)), random_state=SEED); labels = y.loc[sample.index]
    pcs = PCA(n_components=2, random_state=SEED).fit_transform(sample.fillna(sample.median()))
    plt.figure(figsize=(8, 6)); plt.scatter(pcs[:, 0], pcs[:, 1], c=labels, s=5, cmap="tab10", alpha=.6); plt.title("PCA projection"); plt.colorbar(); plt.tight_layout(); plt.savefig(FIG / "pca.png"); plt.close()
    return summary


def main() -> None:
    """Run cleaning, feature analysis, RF tuning, evaluation, and reporting."""
    setup()
    try:
        train_raw, test_raw = download_data()
        summary = save_eda(train_raw)
        # Preserve the source test partition for unbiased final testing; cleaning uses train data statistics.
        train = train_raw.drop_duplicates().replace([np.inf, -np.inf], np.nan)
        test = test_raw.replace([np.inf, -np.inf], np.nan)
        X, target = train.iloc[:, :-1].apply(pd.to_numeric, errors="coerce"), train.iloc[:, -1].astype(int)
        Xt, yt = test.iloc[:, :-1].apply(pd.to_numeric, errors="coerce"), test.iloc[:, -1].astype(int)
        X = X.loc[:, X.var(skipna=True).fillna(0) > 1e-8]
        Xt = Xt[X.columns]
        X.assign(label=target).to_csv(PROC / "cleaned_train.csv", index=False)
        Xt.assign(label=yt).to_csv(PROC / "cleaned_test.csv", index=False)
        imputer = SimpleImputer(strategy="median")
        Xi = imputer.fit_transform(X); Xti = imputer.transform(Xt)
        # Feature selection candidates: variance filtering, mutual information, RF importance; select by validation macro-F1.
        # Rank features on a reproducible stratified subset to keep the full workflow practical.
        rank_idx, _ = train_test_split(np.arange(len(target)), train_size=min(500, len(target)),
                                       random_state=SEED, stratify=target)
        LOG.info("Ranking features on %d stratified training beats", len(rank_idx))
        Xrank, yrank = Xi[rank_idx], target.iloc[rank_idx]
        mi = mutual_info_classif(Xrank, yrank, n_neighbors=3, random_state=SEED)
        rf_probe = RandomForestClassifier(n_estimators=25, max_samples=.75,
                                          class_weight="balanced_subsample", n_jobs=1, random_state=SEED)
        rf_probe.fit(Xrank, yrank)
        LOG.info("Compared mutual-information and Random Forest feature rankings")
        k = min(100, Xi.shape[1])
        ranks = [np.argsort(mi)[::-1][:k], np.argsort(rf_probe.feature_importances_)[::-1][:k]]
        xfit, xval, yfit, yval = train_test_split(Xrank, yrank, test_size=.2, random_state=SEED, stratify=yrank)
        scores = []
        for indices in ranks:
            model = RandomForestClassifier(n_estimators=200, class_weight="balanced_subsample", n_jobs=1, random_state=SEED)
            model.fit(xfit[:, indices], yfit)
            scores.append(f1_score(yval, model.predict(xval[:, indices]), average="macro"))
        selected_idx = ranks[int(np.argmax(scores))]
        selector_mask = np.isin(np.arange(Xi.shape[1]), selected_idx)
        Xi, Xti = Xi[:, selector_mask], Xti[:, selector_mask]
        scaler = StandardScaler().fit(Xi)
        Xs, Xts = scaler.transform(Xi), scaler.transform(Xti)
        rf = RandomForestClassifier(class_weight="balanced_subsample", n_jobs=1, random_state=SEED)
        pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")),
                             ("selector", FixedFeatureSelector(selected_idx.tolist())),
                             ("scaler", StandardScaler()), ("model", rf)])
        param = {"model__n_estimators": [50, 80, 120], "model__max_depth": [None, 12, 20, 30, 45],
                 "model__min_samples_leaf": [1, 2, 4, 8], "model__min_samples_split": [2, 5, 10, 20],
                 "model__max_features": ["sqrt", "log2", .4, .7], "model__bootstrap": [True, False]}
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        search_idx, _ = train_test_split(np.arange(len(target)), train_size=min(5000, len(target)),
                                         random_state=SEED, stratify=target)
        best_params: dict[str, Any] | None = None
        best_cv_score = -1.0
        stale_trials = 0
        # One randomized candidate per search call enables the five-trial patience rule.
        for trial in range(100):
            search = RandomizedSearchCV(pipeline, param, n_iter=1, scoring="f1_macro", cv=cv, n_jobs=1,
                                        random_state=SEED + trial, refit=False,
                                        return_train_score=False, error_score="raise")
            search.fit(X.iloc[search_idx], target.iloc[search_idx])
            trial_score = float(search.best_score_)
            if trial_score - best_cv_score >= 0.001:
                best_cv_score = trial_score
                best_params = search.best_params_
                stale_trials = 0
            else:
                stale_trials += 1
            LOG.info("Randomized search trial %d/100: macro F1 %.4f; best %.4f", trial + 1, trial_score, best_cv_score)
            if stale_trials >= 5:
                LOG.info("Stopping after five trials without >=0.1%% improvement")
                break
        if best_params is None:
            raise RuntimeError("RandomizedSearchCV did not produce a valid candidate")
        LOG.info("Hyperparameter search complete; refitting best model on full training split")
        best = pipeline.set_params(**best_params).fit(X, target)
        pred = best.predict(Xt)
        labels = sorted(np.unique(target))
        metrics = {"accuracy": accuracy_score(yt, pred), "precision_macro": precision_score(yt, pred, average="macro", zero_division=0),
                   "recall_macro": recall_score(yt, pred, average="macro", zero_division=0), "f1_macro": f1_score(yt, pred, average="macro"),
                   "cv_best_macro_f1": best_cv_score, "best_params": best_params, "classification_report": classification_report(yt, pred, zero_division=0)}
        (METRICS / "evaluation.json").write_text(json.dumps(metrics, indent=2, default=float), encoding="utf-8")
        ConfusionMatrixDisplay.from_predictions(yt, pred); plt.tight_layout(); plt.savefig(FIG / "confusion_matrix.png"); plt.close()
        proba = best.predict_proba(Xt)
        ybin = label_binarize(yt, classes=labels)
        plt.figure(figsize=(8, 6))
        for i, label in enumerate(labels):
            fpr, tpr, _ = roc_curve(ybin[:, i], proba[:, i]); plt.plot(fpr, tpr, label=f"Class {label} AUC={auc(fpr,tpr):.3f}")
        plt.plot([0, 1], [0, 1], "k--"); plt.legend(fontsize=7); plt.title("One-vs-rest ROC"); plt.tight_layout(); plt.savefig(FIG / "roc_curve.png"); plt.close()
        plt.figure(figsize=(8, 6))
        for i, label in enumerate(labels):
            p, r, _ = precision_recall_curve(ybin[:, i], proba[:, i]); plt.plot(r, p, label=f"Class {label} AP={average_precision_score(ybin[:, i], proba[:, i]):.3f}")
        plt.legend(fontsize=7); plt.title("Precision-recall curves"); plt.tight_layout(); plt.savefig(FIG / "precision_recall.png"); plt.close()
        feat_names = X.columns.to_numpy()[selector_mask]
        imp = best.named_steps["model"].feature_importances_
        order = np.argsort(imp)[-25:]
        plt.figure(figsize=(9, 7)); plt.barh(feat_names[order], imp[order]); plt.title("Random Forest feature importance"); plt.tight_layout(); plt.savefig(FIG / "feature_importance.png"); plt.close()
        curve_idx, _ = train_test_split(np.arange(len(target)), train_size=min(12000, len(target)),
                                        random_state=SEED, stratify=target)
        sizes, train_scores, val_scores = learning_curve(best, X.iloc[curve_idx], target.iloc[curve_idx], cv=cv, scoring="f1_macro", train_sizes=np.linspace(.2, 1, 5), n_jobs=1)
        plt.figure(); plt.plot(sizes, train_scores.mean(axis=1), "o-", label="Training"); plt.plot(sizes, val_scores.mean(axis=1), "o-", label="CV"); plt.legend(); plt.title("Learning curve (macro F1)"); plt.tight_layout(); plt.savefig(FIG / "learning_curve.png"); plt.close()
        joblib.dump(best, MODELS / "pipeline.joblib"); joblib.dump(best.named_steps["model"], MODELS / "random_forest.joblib")
        joblib.dump(best.named_steps["scaler"], MODELS / "scaler.joblib"); joblib.dump({"selected_feature_mask": selector_mask, "feature_names": list(X.columns)}, MODELS / "feature_selector.joblib")
        (REPORT / "literature_survey.md").write_text("""# Literature survey\n\n- Moody, G. B. & Mark, R. G. (2001). The impact of the MIT-BIH Arrhythmia Database. *IEEE Engineering in Medicine and Biology Magazine*, 20(3), 45–50. The database provides a widely used benchmark for arrhythmia analysis.\n- de Chazal, P., O'Dwyer, M. & Reilly, R. B. (2004). Automatic classification of heartbeats using ECG morphology and heartbeat interval features. *IEEE Transactions on Biomedical Engineering*, 51(7), 1196–1206. Demonstrates the value of morphology and interval features in heartbeat classification.\n- The project uses the Kaggle ECG Heartbeat Categorization dataset (Shayan Fazeli), whose MIT-BIH split contains 187 normalized signal samples per beat and a categorical label. Random Forest is selected for robust nonlinear classification and interpretable feature importance.\n\nThis is a compact undergraduate survey; verify citation formatting and dataset license before publication.\n""", encoding="utf-8")
        report = "# ECG Arrhythmia Classification Results\n\n## Dataset\n\n" + json.dumps(summary, indent=2) + "\n\n## Model\n\nRandomForestClassifier, stratified five-fold randomized search optimizing macro F1.\n\n## Results\n\n" + "\n".join(f"- **{k}:** {v}" for k, v in metrics.items() if k != "classification_report") + "\n\n## Classification report\n\n```text\n" + metrics["classification_report"] + "```\n"
        (REPORT / "final_report.md").write_text(report, encoding="utf-8")
        doc = Document(); doc.add_heading("ECG Arrhythmia Classification", 0); doc.add_paragraph("Random Forest evaluation report")
        doc.add_heading("Dataset", 1); doc.add_paragraph(json.dumps(summary, indent=2)); doc.add_heading("Evaluation", 1)
        for key, value in metrics.items():
            if key != "classification_report": doc.add_paragraph(f"{key}: {value}")
        doc.add_heading("Classification report", 1); doc.add_paragraph(metrics["classification_report"]); doc.save(REPORT / "final_report.docx")
        pdf = canvas.Canvas(str(REPORT / "final_report.pdf"), pagesize=letter); text = pdf.beginText(45, 750); text.setFont("Helvetica", 10)
        for line in ("ECG Arrhythmia Classification Results", "", *report.replace("#", "").replace("**", "").splitlines()):
            for segment in [line[i:i+100] for i in range(0, len(line), 100)] or [""]:
                if text.getY() < 50: pdf.drawText(text); pdf.showPage(); text = pdf.beginText(45, 750); text.setFont("Helvetica", 10)
                text.textLine(segment)
        pdf.drawText(text); pdf.save()
        prs = Presentation()
        slides = [("ECG Arrhythmia Classification", "Random Forest end-to-end study"), ("Research motivation", "Automated heartbeat categorization supports ECG analysis."),
                  ("Dataset", json.dumps(summary, indent=2)), ("Classes", "Five heartbeat classes; class imbalance is substantial."),
                  ("Data preparation", "Missing values: median imputation. Duplicates removed from training data. Constant features filtered."),
                  ("Exploratory analysis", "Class balance, distributions, correlation and PCA are in outputs/figures."),
                  ("Feature selection", "Compared mutual information and Random Forest feature rankings on a stratified validation split."),
                  ("Model", "RandomForestClassifier with balanced subsampling."), ("Hyperparameter search", f"RandomizedSearchCV: up to 100 settings, stratified 5-fold, best CV macro F1 {best_cv_score:.4f}."),
                  ("Evaluation", "Held-out source test set; see confusion matrix, ROC and precision-recall curves."),
                  ("Results", "\n".join(f"{k}: {v:.4f}" for k,v in metrics.items() if isinstance(v, (float,int)))),
                  ("Conclusion", "Model artifacts, figures, metrics and reports are saved in the project outputs.")]
        for title, body in slides:
            sl = prs.slides.add_slide(prs.slide_layouts[1]); sl.shapes.title.text = title; sl.placeholders[1].text = body
            for para in sl.placeholders[1].text_frame.paragraphs:
                for run in para.runs: run.font.size = Pt(18)
        prs.save(REPORT / "presentation.pptx")
        LOG.info("Completed. Metrics: %s", metrics)
    except Exception:
        LOG.exception("Training pipeline failed")
        raise


if __name__ == "__main__":
    main()
