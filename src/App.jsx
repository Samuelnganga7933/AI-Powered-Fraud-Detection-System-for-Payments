import { useMemo, useState } from "react";
import { predictTransaction } from "./api";
const featureNames = [
  "Transaction amount", "Transaction frequency", "Recipient blacklist status", "Device fingerprinting",
  "VPN or proxy usage", "Behavioral biometrics", "Time since last transaction", "Social trust score",
  "Account age", "High-risk transaction times", "Past fraudulent behavior flags", "Location-inconsistent transactions",
  "Normalized transaction amount", "Transaction context anomalies", "Fraud complaints count", "Merchant category mismatch",
  "User daily limit exceeded", "Recent high-value transaction flags", "Recipient status: suspicious", "Recipient status: verified",
  "Geo flag: normal", "Geo flag: unusual",
];

const starterValues = [0.007772, 0.461538, 0, 0, 0, 0.119084, 0.794263, 0.172174, 0.786936, 0, 0, 0, 0.414003, 0.186907, 0, 0, 0, 0, 0, 1, 1, 0];

export default function App() {
  const [values, setValues] = useState(starterValues);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const fraudPercent = useMemo(() => result ? Math.round(result.fraud_probability * 100) : null, [result]);

  function updateValue(index, value) {
    setValues((current) => current.map((item, position) => position === index ? value : item));
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");
    try {
      setResult(await predictTransaction(values));
    } catch (requestError) {
      setError(`${requestError.message}. Is the Flask API running?`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">SAFEPAYAI / INFERENCE CONSOLE</p>
          <h1>Screen a payment before it settles.</h1>
          <p className="lede">A transparent demo client for the bundled Random Forest model. Enter the model&apos;s normalized feature vector and inspect the returned risk score.</p>
        </div>
        <div className="status"><span /> API contract: 22 features</div>
      </section>

      <form className="panel" onSubmit={submit}>
        <div className="panel-heading"><div><p className="eyebrow">TRANSACTION SIGNALS</p><h2>Feature vector</h2></div><span className="muted">Values are sent as numeric inputs</span></div>
        <div className="feature-grid">
          {featureNames.map((name, index) => (
            <label className="field" key={name}>
              <span>{String(index + 1).padStart(2, "0")} · {name}</span>
              <input type="number" step="any" value={values[index]} onChange={(event) => updateValue(index, event.target.value)} required />
            </label>
          ))}
        </div>
        <button type="submit" disabled={loading}>{loading ? "Evaluating…" : "Evaluate transaction"}</button>
      </form>

      {error && <div className="alert">{error}</div>}
      {result && <section className={`result ${result.prediction === 1 ? "danger" : "safe"}`}><div><p className="eyebrow">MODEL DECISION</p><h2>{result.label === "fraud" ? "Review recommended" : "No fraud signal detected"}</h2><p>{result.label === "fraud" ? "The model classified this vector as potentially fraudulent." : "The model classified this vector as legitimate."}</p></div><strong>{fraudPercent}%<small> fraud probability</small></strong></section>}
      <footer>For research and demonstration only. This output is not a payment authorization decision.</footer>
    </main>
  );
}
