import React from "react";
export default function PredictionResult({ result, preview }) {
  return <section className="panel" aria-label="Model prediction">
    <h2>2. Model prediction</h2>
    {preview && <div className="image-frame"><img className="preview" src={preview} alt="Uploaded retinal image" /></div>}
    {result ? <><p className="prediction-value"><strong>{result.prediction.label}</strong></p><p>Illustrative model confidence: {(result.prediction.confidence * 100).toFixed(1)}%</p><p>Model: {result.prediction.model}</p></> : <div className="empty-state"><span>AWAITING ANALYSIS</span><p>{preview ? 'Image ready. Run the prototype pipeline to explore its outputs.' : 'Upload a retinal image to preview it and explore the model output.'}</p></div>}
  </section>;
}
