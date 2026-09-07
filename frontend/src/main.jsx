import { StrictMode } from 'react' // React ka StrictMode import - development warnings ke liye
import { createRoot } from 'react-dom/client' // DOM mein React component render karne ka function
import App from './App.jsx' // Main App component import - jahan sab routes aur state manage hote hain

createRoot(document.getElementById('root')).render( // 'root' id wale div mein App ko render karta hai
    <StrictMode> // Extra checks aur warnings enable karta hai development mode mein //
    <App /> // App component render - BrowserRouter, Routes, aur sab pages yahan se start hote hain
  </StrictMode>,
)
