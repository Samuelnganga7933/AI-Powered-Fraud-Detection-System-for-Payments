# SafePayAI

A small, end-to-end experiment in making payment risk easier to see.

SafePayAI takes a transaction, scores its risk, and returns something a human can actually inspect. The project pairs a synthetic dataset and Random Forest model with a Flask API and a React console.

## The interesting bit

This is not presented as a production payment control. It is a study in the line between a model and a usable product: input contracts, probability output, health checks, API tests, and rate limiting all matter as much as the prediction itself.

## Stack

`Python` `scikit-learn` `Flask` `React` `Vite` `pytest`

## Start here

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

In a second terminal:

```bash
npm install
npm run dev
```

## What is included

- `/predict` for transaction-risk scoring
- `/health` and `/model-info` for simple operational checks
- A reproducible training script
- Input validation and API tests
- Configurable request rate limiting
- A synthetic dataset and explicit model limitations

## Preview

![SafePayAI system design](./assets/SystemDesign.png)

*System design included with the project.*
## Next

The next useful step is not a bigger model. It is better evaluation: calibrated thresholds, explainable decisions, drift checks, and a clearer review path for uncertain transactions.

[Open the code](https://github.com/Samuelnganga7933/AI-Powered-Fraud-Detection-System-for-Payments)
