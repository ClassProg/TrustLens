import React from "react";
import { useEffect } from 'react';
import { Link } from 'react-router-dom';


const steps = [
  {number:'01', title:'Upload image', text:'Start with a retinal image in PNG or JPG format.'},
  {number:'02', title:'CNN classification', text:'Select a model to explore its predicted class.'},
  {number:'03', title:'XAI explanations', text:'Inspect visual explanations of the model output.'},
  {number:'04', title:'Quantitative evaluation', text:'Compare explanation metrics through Quantus.'},
  {number:'05', title:'Results dashboard', text:'Review outputs and expert disagreement when verified data is available.'},
];
export default function LandingPage() {
  useEffect(() => {
    if (!('IntersectionObserver' in window)) { document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible')); return; }
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {entry.target.classList.add('is-visible');observer.unobserve(entry.target);}
    }), {threshold: 0.12});
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);
  return <div className="site">
    <nav className="site-nav" aria-label="Main navigation">
      <Link className="brand" to="/" aria-label="TrustLens home">TrustLens</Link>
      <div className="nav-links"><a href="#about">About</a><a href="#how">How it works</a><a href="#why">Why TrustLens</a></div>
      <Link className="nav-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link>
    </nav>
    <main>
      <section className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <div className="hero-content reveal is-visible">
          <span className="eyebrow"><span className="status-dot" /> RESEARCH PLATFORM · EXPLAINABLE AI</span>
          <h1>TrustLens</h1>
          <h2 className="hero-statement">See beyond<br/><em>the prediction.</em></h2>
          <p>A research framework for benchmarking explainable AI in retinal imaging. Explore predictions, inspect explanations, and evaluate how they perform.</p>
          <div className="hero-actions"><Link className="primary-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link><a className="secondary-cta" href="#about">Discover the platform <span aria-hidden="true">↓</span></a></div>
          <p className="hero-note">Research prototype · Simulated outputs until model integration. Not a medical diagnostic tool.</p>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit orbit-three"/>
          <div className="lens-core"><div className="lens-inner"><div className="lens-pupil"/></div></div>
          <span className="visual-tag tag-top">EXPLAINABILITY <b>↗</b></span><span className="visual-tag tag-bottom">MODEL INSIGHT <b>↗</b></span>
        </div>
        <div className="hero-bottom">A CLEARER VIEW OF AI <span>SCROLL TO EXPLORE ↓</span></div>
      </section>
      <section className="info-section" id="about"><div className="section-kicker reveal">01 / WHAT IS TRUSTLENS?</div><div className="section-layout"><h2 className="reveal">AI should be<br/><span>understandable.</span></h2><div className="section-copy reveal"><p>TrustLens brings explainable AI research into one workspace for retinal imaging.</p><p>Compare model predictions, inspect visual explanations, and explore quantitative evaluation alongside expert disagreement when verified grading data is available.</p></div></div></section>
      <section className="how-section" id="how"><div className="section-kicker reveal">02 / THE RESEARCH WORKFLOW</div><h2 className="reveal">From image<br/><span>to insight.</span></h2><div className="step-grid">{steps.map(step => <article className="step-card reveal" key={step.number}><div className="step-number">{step.number} <span>↗</span></div><h3>{step.title}</h3><p>{step.text}</p></article>)}</div></section>
      <section className="why-section" id="why">
        <div className="section-kicker reveal">03 / WHY TRUSTLENS?</div>
        <div className="why-intro reveal"><h2>Why explainability<br/><span>matters in medical AI.</span></h2><p>A prediction is a starting point. Research also needs a way to inspect, compare, and question the explanation behind it.</p></div>
        <div className="why-grid">
          <article className="research-card reveal"><span className="card-index">01 / TRANSPARENCY</span><h3>Make outputs inspectable.</h3><p>Bring predictions and visual explanations together so researchers can examine model behavior.</p></article>
          <article className="research-card research-card-featured reveal"><span className="card-index">THE RESEARCH QUESTION</span><h3>How useful is<br/>an explanation?</h3><p>TrustLens connects visual inspection with quantitative benchmarking. Explore what an explanation shows and how it performs under evaluation.</p><a className="secondary-cta" href="#how">Explore the workflow <span aria-hidden="true">↗</span></a></article>
          <article className="research-card reveal"><span className="card-index">02 / EXPLAINABILITY</span><h3>Look beyond a label.</h3><p>Inspect explanation maps to explore which image regions a method highlights.</p></article>
          <article className="research-card reveal"><span className="card-index">03 / BENCHMARKING</span><h3>Ask measurable questions.</h3><p>Explore faithfulness, robustness, and localization with Quantus metrics. Interpretation depends on the evaluation configuration.</p></article>
          <article className="research-card reveal"><span className="card-index">04 / EXPERT DISAGREEMENT</span><h3>Keep human context visible.</h3><p>Review disagreement when verified expert grading data is available. Missing expert data is explicitly identified.</p></article>
        </div>
      </section>
      <section className="closing-section"><div className="closing-orb" aria-hidden="true"/><div className="closing-content reveal"><span className="eyebrow">READY TO EXPLORE?</span><h2>Look closer.</h2><p>Experience the TrustLens research dashboard.</p><Link className="closing-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link></div></section>
    </main><footer className="site-footer"><span>TrustLens · Team explAIn</span><span>Research only · Not for clinical diagnosis</span></footer>
  </div>;
}
