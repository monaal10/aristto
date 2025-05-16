import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import Library from 'pages/Library.jsx';
import Profile from './pages/Profile';
import Login from 'pages/Login';
import Signup from 'pages/Signup';
import ProtectedRoute from 'core/protectedRoute';
import { AuthProvider } from 'context/authContext';
import Chat from 'pages/Chat';
import Pricing from 'pages/Pricing.jsx'
import ResetPassword from 'pages/ResetPassword.jsx'
import { HelmetProvider } from 'react-helmet-async';
import VerifyEmail from 'pages/VerifyEmail.jsx'


function App() {
  return (
    <HelmetProvider>
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/reset-password/:token" element={<ResetPassword />} />
          <Route path="/verify-email/:token" element={<VerifyEmail />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute >
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Home />} />
            <Route path="profile" element={<Profile />} />
            <Route path="library" element={<Library />} />
            <Route path="chat" element={<Chat />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
    </HelmetProvider>
  );
}

export default App;
