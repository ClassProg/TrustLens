import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import LandingPage from './components/LandingPage';
import './App.css';
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><BrowserRouter><Routes><Route path="/" element={<LandingPage/>}/><Route path="/app" element={<App/>}/><Route path="*" element={<LandingPage/>}/></Routes></BrowserRouter></React.StrictMode>);
