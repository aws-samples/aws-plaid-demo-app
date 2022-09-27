import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Authenticator } from "@aws-amplify/ui-react";
import Protected from './pages/Protected';
import Login from './pages/Login';
import Institution from './pages/Institution';
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
                  <Protected />
                </RequireAuth>
              }
            />
            <Route
              path="/institution/:id"
              element={
                <RequireAuth>
                  <Institution />
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
