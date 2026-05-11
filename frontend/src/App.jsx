import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PartnerSelect from './pages/PartnerSelect'
import ChatPage from './pages/ChatPage'
import ParentReport from './pages/ParentReport'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PartnerSelect />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/parent" element={<ParentReport />} />
      </Routes>
    </BrowserRouter>
  )
}
