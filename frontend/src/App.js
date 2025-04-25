import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Authenticator } from "@aws-amplify/ui-react";
import Login from './pages/Login';
import AccountManagement from './pages/AccountManagement';
import InvestmentDashboard from './pages/InvestmentDashboard';
import Layout from './components/Layout';
import RequireAuth from './RequireAuth';

import './App.css';

function App() {
  return (
    <Authenticator.Provider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route
              index
              element={
                <RequireAuth>
                  <AccountManagement />
                </RequireAuth>
              }
            />
            <Route
              path="/investments"
              element={
                <RequireAuth>
                  <InvestmentDashboard />
                </RequireAuth>
              }
            />
            <Route path="/login" element={<Login />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </Authenticator.Provider>
  );
}

export default App;
