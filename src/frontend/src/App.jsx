import React from "react";
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import webLogo from './assets/weblogo.png';
import { analyze, getHealth, getModels } from './services/api';
import UploadPanel from './components/UploadPanel';
import PredictionResult from './components/PredictionResult';
import ExplanationPanel from './components/ExplanationPanel';
import QuantusReport from './components/QuantusReport';
import ExpertDisagreement from './components/ExpertDisagreement';
export default function App() {
  const [health, setHealth] = useState(null), [models, setModels] = useState([{id:'resnet50',name:'ResNet-50'},{id:'densenet121',name:'DenseNet-121'}]);
  const [file, setFile] = useState(null), [model, setModel] = useState('resnet50');
  const [preview, setPreview] = useState(null), [result, setResult] = useState(null);
  const [error, setError] = useState(''), [loading, setLoading] = useState(false);
  useEffect(() => { getHealth().then(setHealth).catch(() => setHealth({status:'offline'})); getModels().then(setModels).catch(() => {}); }, []);
  useEffect(() => { if (!file) {setPreview(null);return;} const url = URL.createObjectURL(file);setPreview(url);return () => URL.revokeObjectURL(url); }, [file]);
  function chooseFile(next) {setResult(null);setError('');if (next && !['image/png','image/jpeg'].includes(next.type)) {setFile(null);setError('Please choose a PNG or JPG image.');return;}setFile(next);}
  async function run() {if (!file) return;setLoading(true);setError('');setResult(null);try {setResult(await analyze(file, model));}catch(e){setError(e.message);}finally{setLoading(false);}}
  return <div className="dashboard-shell"><nav className="dashboard-nav" aria-label="Workspace navigation"><Link to="/" className="brand"><img className="brand-logo" src={webLogo} alt="" />TrustLens</Link><Link to="/" className="back-link">← Back to website</Link></nav><main className="dashboard-main"><div className="dashboard-heading"><span className="section-kicker">RESEARCH WORKSPACE</span><h1>Image analysis</h1><p>Explore retinal image predictions, visual explanations, and evaluation metrics in one research workspace.</p></div><p className="notice prototype-notice"><strong>Prototype workspace · Mock outputs</strong><br/>The AI pipeline is a skeleton until trained model checkpoints and evaluation are integrated. Outputs are illustrative and do not provide medical diagnoses or clinical decisions.</p><p className="backend-status" role="status">Backend: <strong>{health?.status === 'ok' ? 'Connected' : 'Offline / checking…'}</strong></p>{error && <div role="alert" className="error">{error} <button onClick={run} disabled={!file || loading}>Try again</button></div>}
    <div className="two"><UploadPanel file={file} onFile={chooseFile} model={model} onModel={m=>{setModel(m);setResult(null);}} models={models} onAnalyze={run} loading={loading}/><PredictionResult result={result} preview={preview}/></div>
    {result && <>{result.demo_mode && <p className="notice">DEMO MODE: predictions and scores are simulated; no AI analysis was performed. Explanation images are illustrative.</p>}<h2 className="result-heading">Explanation methods</h2><div className="three">{result.explanations.map(e => <ExplanationPanel key={e.method} explanation={e}/>)}</div><div className="two"><QuantusReport quantus={result.quantus}/><ExpertDisagreement data={result.expert_disagreement}/></div></>}
    <footer className="dashboard-footer">TrustLens benchmarks AI explanations for research. It does not provide medical diagnoses.</footer></main></div>;
}
