import React from "react";
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from "react-router-dom";

const steps = [
  {number:'01', title:'Upload', text:'Choose a retinal image in PNG or JPG format.'},
  {number:'02', title:'Analyze', text:'Select an AI model and run the pipeline.'},
  {number:'03', title:'Explore', text:'Review predictions, explanations, and evaluation scores.'},
];
export default function LandingPage() {
  const navigate = useNavigate();
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
      <Link className="brand" to="/" aria-label="TrustLens home"><span className="brand-icon">✳</span> TrustLens<span className="brand-dot">.</span></Link>
      <div className="nav-links"><a href="#about">About</a><a href="#how">How it works</a><a href="#why">Why TrustLens</a></div>
      <Link className="nav-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link>
    </nav>
    <main>
      <section className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <div className="hero-content reveal is-visible">
          <span className="eyebrow"><span className="status-dot" /> RESEARCH PLATFORM · EXPLAINABLE AI</span>
          <h1>See beyond<br/><em>the prediction.</em></h1>
          <p>Understand how AI reads medical images — and explore how reliable its explanations really are.</p>
          <div className="hero-actions"><Link className="primary-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link><a className="secondary-cta" href="#about">Discover the platform <span aria-hidden="true">↓</span></a></div>
          <p className="hero-note">Built for research. Not a medical diagnostic tool.</p>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit orbit-three"/>
          <div className="lens-core"><div className="lens-inner"><div className="lens-pupil"/></div></div>
          <span className="visual-tag tag-top">EXPLAINABILITY <b>↗</b></span><span className="visual-tag tag-bottom">MODEL INSIGHT <b>✳</b></span>
        </div>
        <div className="hero-bottom">A CLEARER VIEW OF AI <span>SCROLL TO EXPLORE ↓</span></div>
      </section>
      <section className="info-section" id="about"><div className="section-kicker reveal">01 / WHAT IS TRUSTLENS?</div><div className="section-layout"><h2 className="reveal">AI should be<br/><span>understandable.</span></h2><div className="section-copy reveal"><p>TrustLens is a research tool for exploring AI predictions in retinal images.</p><p>It brings predictions, visual explanations, and evaluation scores into one simple dashboard.</p></div></div></section>
      <section className="how-section" id="how"><div className="section-kicker reveal">02 / HOW TO USE IT</div><h2 className="reveal">Three steps.<br/><span>One clearer picture.</span></h2><div className="step-grid">{steps.map(step => <article className="step-card reveal" key={step.number}><div className="step-number">{step.number} <span>↗</span></div><h3>{step.title}</h3><p>{step.text}</p></article>)}</div></section>
      <section className="why-section" id="why"><div className="section-kicker reveal">03 / WHY IT MATTERS</div><div className="why-layout"><div className="reveal"><h2>More than<br/><span>an answer.</span></h2><p>Accuracy is only part of the story. TrustLens helps researchers ask why a model made a prediction and how its explanations perform.</p></div><div className="why-points reveal"><div><span>01</span><strong>Visual clarity</strong><p>See what influenced a prediction.</p></div><div><span>02</span><strong>Measurable explanations</strong><p>Explore faithfulness, robustness, and localization.</p></div><div><span>03</span><strong>Research comparison</strong><p>Compare AI models and expert agreement when data is available.</p></div></div></div></section>
      <section className="closing-section"><div className="closing-orb" aria-hidden="true"/><div className="closing-content reveal"><span className="eyebrow">READY TO EXPLORE?</span><h2>Look closer.</h2><p>Experience the TrustLens research dashboard.</p><Link className="closing-cta" to="/app">Try TrustLens <span aria-hidden="true">↗</span></Link></div></section>
    </main><footer className="site-footer"><span>✳ TrustLens · Team explAIn</span><span>Research only · Not for clinical diagnosis</span></footer>
  </div>;
}
