import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import DemoDashboard from './components/DemoDashboard';
import LandingPage from './components/LandingPage';
import './App.css';
const Workspace = import.meta.env.VITE_TRUSTLENS_DEMO_MODE === 'false' ? App : DemoDashboard;

ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><BrowserRouter><Routes><Route path="/" element={<LandingPage/>}/><Route path="/app" element={<Workspace/>}/><Route path="*" element={<LandingPage/>}/></Routes></BrowserRouter></React.StrictMode>);
