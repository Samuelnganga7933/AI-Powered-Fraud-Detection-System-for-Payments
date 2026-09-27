# Development timeline and provenance

This document records what can be established from the repository itself. Notebook execution timestamps are evidence of notebook activity; they are not treated as proof of every surrounding coding activity. Git dates are taken directly from the repository history.

## Observed notebook activity

The notebooks identify the execution author as `shadabkhan pathan` and contain Google Colab execution metadata in UTC.

| Recorded timestamp (UTC) | Notebook evidence | Milestone supported |
| --- | --- | --- |
| 2024-12-14 12:46–13:03 | `DataSetGeneratorUSingNumpy.ipynb`, cells 0–2 and 4 | Dataset inspection, preprocessing setup, and synthetic data generation work |
| 2024-12-15 10:35 | `DataSetGeneratorUSingNumpy.ipynb`, cell 5 | Additional dataset/preprocessing generation work |
| 2024-12-15 09:55–10:14 | `FraudDetectionUSingGAN.ipynb`, cells 2–7 and 10–15 | GAN augmentation, augmented data preparation, Random Forest training, tuning, and metric evaluation |
| 2024-12-15 11:41–11:46 | `FraudDetectionUSingGAN.ipynb`, cells 0–1 | Dataset inspection and feature preprocessing rerun |
| 2024-12-18 08:52 | `FraudDetectionUSingGAN.ipynb`, cell 8 | Follow-up synthetic-data inspection or experiment rerun; the exact purpose is not recoverable from the timestamp alone |

## Code-structure milestones supported by the notebooks

- A synthetic transaction dataset was generated with 20,000 rows.
- Numerical features were normalized with `MinMaxScaler`.
- Categorical features were one-hot encoded with `drop_first=True`.
- The processed feature matrix contained 22 features.
- The original train/test split was 16,000 / 4,000 rows.
- GAN experimentation produced an augmented 17,000-row feature set and a 13,600 / 3,400 validation split.
- A Random Forest classifier was trained and tuned.
- The notebook output recorded 97.09% accuracy, 0.97 precision, 0.97 recall, 0.97 F1, and 1.00 ROC-AUC for one validation run.
- The notebook output recorded a saved model named `best_rf_model.pkl`.

## Observed Git history

| Date | Commit | Event |
| --- | --- | --- |
| 2026-03-26 | `7ce6740` | Initial repository and license/README added |
| 2026-03-26 | `189b51b` | README expanded |
| 2026-03-26 | `d179b8e` | Notebook, dataset, model, API, frontend, and design artifacts uploaded |
| 2026-09-08 | `7d3227c` | Funding metadata added |
| 2026-09-27 | Current refactor commits | API, frontend, documentation, tests, source-language configuration, and reproducible scripts added |

## Interpretation

The strongest defensible project start date is **2024-12-14**, when the first recorded notebook execution occurred. The GitHub repository itself was assembled on **2026-03-26**. The evidence supports a research/modeling phase in December 2024 and a later repository-publication phase in March 2026; it does not establish continuous development on every intervening date.

The current project is complete as a documented portfolio/demo system. It is not a production fraud platform because authentication, monitoring, independent temporal evaluation, model governance, and operational deployment are outside the repository scope.

## Reproduce the extraction

```bash
python scripts/extract_notebook_timeline.py \
  DataSetGeneratorUSingNumpy.ipynb \
  FraudDetectionUSingGAN.ipynb
```

The extractor reports metadata recorded inside the notebooks and deliberately leaves Git commit timestamps unchanged.
