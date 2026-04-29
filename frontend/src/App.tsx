import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Navbar from "./components/Navbar"
import HeroSection from "./components/HeroSection"
import Dashboard from "./components/Dashboard"

function App() {
  return (
    <Router>
      <div className="bg-hero-bg min-h-screen selection:bg-primary selection:text-primary-foreground">
        <Navbar />
        <Routes>
          <Route path="/" element={<HeroSection />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
