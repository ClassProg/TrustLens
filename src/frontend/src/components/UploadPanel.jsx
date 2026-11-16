import React from "react";
export default function UploadPanel({ file, onFile, model, onModel, models, onAnalyze, loading }) {
  return <section className="panel"><h2>1. Input &amp; model</h2><p className="panel-hint">Choose a retinal image and a classification model to explore the prototype pipeline.</p><label>Retinal image (PNG/JPG)<input type="file" accept=".png,.jpg,.jpeg,image/png,image/jpeg" onChange={e => onFile(e.target.files[0] || null)} /></label>
    <label>Classification model<select value={model} onChange={e => onModel(e.target.value)}>{models.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></label>
    <button aria-busy={loading} disabled={!file || loading} onClick={onAnalyze}>{loading ? 'Analyzing…' : 'Analyze image'}</button></section>;
}