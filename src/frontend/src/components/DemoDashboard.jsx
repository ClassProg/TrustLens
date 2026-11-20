import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import webLogo from '../assets/weblogo.png';
import { demoResults } from '../demoResults';
import './DemoDashboard.css';

function DemoResults() {
  const [unavailableImages, setUnavailableImages] = useState({});
  const { explanations, evaluationMethods, evaluation } = demoResults;

  return (
    <>
      <section aria-labelledby="demo-explanations">
        <h2 className="result-heading" id="demo-explanations">Simulated results · Example explanations</h2>
        <p className="demo-note">Example explanations from a reference retinal image. These visualizations were not generated from the uploaded image.</p>
        <div className="three">
          {explanations.map(({ label, image }) => (
            <article className="panel demo-explanation" key={label}>
              <h3>{label}</h3>
              {unavailableImages[image] ? (
                <div className="empty-state"><p>Reference image unavailable.</p></div>
              ) : (
                <div className="demo-reference">
                  <img
                    src={import.meta.env.BASE_URL + 'assets/' + image}
                    alt={`${label} example from the reference retinal image`}
                    onError={() => setUnavailableImages(previous => ({ ...previous, [image]: true }))}
                  />
                </div>
              )}
            </article>
          ))}
        </div>
      </section>
      <section className="panel demo-evaluation" aria-labelledby="demo-evaluation">
        <h2 id="demo-evaluation">Explainability Evaluation — Simulated Quantus Results</h2>
        <p>These fictional scores illustrate the dashboard. Quantus did not produce them.</p>
        <table className="demo-table" aria-labelledby="demo-evaluation">
          <thead>
            <tr>
              <th scope="col">Metric</th>
              {evaluationMethods.map(method => <th key={method} scope="col">{method}</th>)}
            </tr>
          </thead>
          <tbody>
            {evaluation.map(({ metric, scores }) => (
              <tr key={metric}>
                <th scope="row">{metric}</th>
                {scores.map((score, index) => <td key={evaluationMethods[index]}>{score}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
        <p>Actual Quantus metrics have specific definitions, scales, and scoring directions. These example scores do not establish clinical reliability.</p>
      </section>
    </>
  );
}

export default function DemoDashboard() {
  const [upload, setUpload] = useState(null);
  const [phase, setPhase] = useState('idle');
  const [error, setError] = useState('');
  const { prediction } = demoResults;

  useEffect(() => {
    if (upload) return () => URL.revokeObjectURL(upload.url);
  }, [upload]);

  useEffect(() => {
    if (phase !== 'analyzing') return;
    const timer = window.setTimeout(() => setPhase('complete'), 2000);
    return () => window.clearTimeout(timer);
  }, [phase, upload]);

  function chooseImage(event) {
    const [file] = event.target.files;
    event.target.value = '';
    if (!file) return;

    setError('');
    setPhase('idle');
    if (file.type && !file.type.startsWith('image/')) {
      rejectImage();
      return;
    }
    setUpload({ name: file.name, url: URL.createObjectURL(file) });
  }

  function rejectImage() {
    setUpload(null);
    setPhase('idle');
    setError('Choose a valid image that your browser can display.');
  }

  return (
    <div className="dashboard-shell">
      <nav className="dashboard-nav" aria-label="Workspace navigation">
        <Link to="/" className="brand"><img className="brand-logo" src={webLogo} alt="" />TrustLens</Link>
        <Link to="/" className="back-link">← Back to website</Link>
      </nav>
      <aside className="demo-banner"><strong>DEMO MODE — Simulated results. Not for clinical use.</strong></aside>
      <main className="dashboard-main demo-main">
        <header className="dashboard-heading">
          <h1>Image analysis</h1>
          <p>Choose an image to preview the TrustLens results dashboard. Your image stays in this browser tab.</p>
        </header>
        {error && <p role="alert" className="error">{error}</p>}
        <div className="two demo-overview">
          <section className="panel">
            <h2>Image preview</h2>
            <label>Choose an image
              <input type="file" accept="image/*" onChange={chooseImage} />
            </label>
            {upload && (
              <figure className="demo-preview">
                <div className="image-frame">
                  <img className="preview" key={upload.url} src={upload.url} alt="Uploaded image preview"
                    onLoad={() => setPhase('analyzing')} onError={rejectImage} />
                </div>
                <figcaption>{upload.name}</figcaption>
              </figure>
            )}
          </section>
          <section className="panel demo-prediction" aria-labelledby="demo-prediction">
            <h2 id="demo-prediction">Simulated Prediction</h2>
            <div role="status">
              {phase === 'complete' ? (
                <>
                  <p className="demo-prediction-value"><strong>{prediction.label}</strong></p>
                  <dl className="demo-prediction-details">
                    <div><dt>Model</dt><dd>{prediction.model}</dd></div>
                    <div><dt>Example confidence</dt><dd>{prediction.confidence}</dd></div>
                  </dl>
                  <p>The confidence is a fixed example value. No probability is calculated from your image.</p>
                </>
              ) : (
                <div className="empty-state">
                  {phase === 'analyzing' && <span className="demo-spinner" aria-hidden="true" />}
                  <p>{phase === 'analyzing' ? 'Simulating analysis…' : 'Choose an image to see the simulated prediction.'}</p>
                </div>
              )}
            </div>
          </section>
        </div>
        {phase === 'complete' && <DemoResults />}
      </main>
    </div>
  );
}
