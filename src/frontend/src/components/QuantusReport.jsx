import React from "react";
export default function QuantusReport({ quantus }) {
  return <section className="panel"><h2>Quantus evaluation</h2><p>Source: <strong>{quantus.source}</strong></p>
    {['faithfulness', 'robustness', 'localization'].map(k => <div className="metric" key={k}><label htmlFor={`metric-${k}`}>{k}<span>{quantus[k]}</span></label><progress id={`metric-${k}`} value={quantus[k]} max="1" /></div>)}
    <small>Scores shown are illustrative until real evaluation is integrated. Metric interpretation depends on the chosen Quantus configuration.</small>
  </section>;
}
