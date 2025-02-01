import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
// import CompanyRegistration from './components/CompanyPortal'
import CompanyPortal from './components/CompanyPortal'
import MarketingAnalysis from './components/MarketingAnalysis'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      {/* <CompanyPortal/> */}
      <MarketingAnalysis/>
    </>
  )
}

export default App
