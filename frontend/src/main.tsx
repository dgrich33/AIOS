import React from 'react';
import { createRoot } from 'react-dom/client';
import { ApiProvider } from './api';
import { App } from './App';
import './style.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ApiProvider>
      <App />
    </ApiProvider>
  </React.StrictMode>,
);
