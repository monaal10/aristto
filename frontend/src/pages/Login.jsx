import React, { useState } from 'react';
import { ChevronRight, Eye, EyeOff } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useAuth } from 'context/AuthContext';
import apiClient from 'config/apiConfig.js'

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [isResetting, setIsResetting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await login(formData);

      if (result.success) {
        // Check user profile to determine navigation
        const response = await apiClient.get('/user/profile', { withCredentials: true });
        const dateCreated = new Date(response.data.date_created.$date);
        const daysSinceCreation = (new Date() - dateCreated) / (1000 * 60 * 60 * 24);

        if (result.user.plan !== "pro") {
          if (daysSinceCreation <= 3000) {
            navigate('/');
          } else {
            navigate('/pricing');
          }
          return;
        }

        // Navigate to the attempted page or home
        const from = location.state?.from?.pathname || '/';
        navigate(from, { replace: true });
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setIsResetting(true);

    try {
      const response = await apiClient.post('/user/reset-password', {
        email: resetEmail
      });

      const data = await response.data;

      if (response.status === 200) {
        toast.success('Password reset link sent to your email!');
        setShowForgotPassword(false);
        setResetEmail('');
      } else {
        toast.error(data.message || 'Failed to send reset link');
      }
    } catch (error) {
      toast.error('An error occurred while requesting password reset');
    } finally {
      setIsResetting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePasswordToggle = () => {
    setShowPassword((prev) => !prev);
  };

  return (
    <div className="flex justify-center items-center min-h-screen p-4"
         style={{ background: 'linear-gradient(to bottom, #FFFFFF 23%, #E1E9EF 100%)' }}>
      <ToastContainer />
      <div className="flex flex-col md:flex-row w-full max-w-4xl rounded-lg overflow-hidden shadow-lg">
        {/* Left Panel - Login Form */}
        <div className="w-full md:w-1/2 p-6 md:p-8 flex flex-col justify-center">
          <h2 className="text-xl md:text-2xl font-semibold mb-6">Login to Your Account</h2>

          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#E1E9EF]"
              required
              disabled={isLoading}
            />
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#E1E9EF] w-full"
                required
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={handlePasswordToggle}
                className="absolute inset-y-0 right-4 flex items-center text-gray-500"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            <div className="flex justify-between items-center mb-2">
              <button
                type="button"
                onClick={() => setShowForgotPassword(true)}
                className="text-sm text-[#234869] hover:text-[#E1E9EF]"
              >
                Forgot Password?
              </button>
            </div>
            <button
              type="submit"
              className="bg-[#234869] text-white p-3 rounded-lg font-medium hover:bg-[#E1E9EF] hover:text-[#234869]"
              disabled={isLoading}
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        </div>

        {/* Right Panel - New User */}
        <div className="w-full md:w-1/2 bg-[#234869] p-6 md:p-8 flex flex-col justify-center items-start text-white">
          <img src="/WhiteLogo.png" alt="Aristto" className="mb-4 w-40 h-auto" />
          <h3 className="text-2xl md:text-3xl font-semibold mb-4 font-open-sans">New Here?</h3>
          <p className="mb-6 md:mb-8 text-teal-50 font-open-sans">
            Get answers to your research questions!
          </p>
          <button
            onClick={() => navigate('/signup')}
            className="px-6 py-2 rounded-lg border-2 border-white text-white font-medium hover:bg-#E1E9EF hover:text-[##234869] flex items-center gap-2"
            disabled={isLoading}
          >
            Sign Up
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
          <div className="bg-white p-6 md:p-8 rounded-lg w-full max-w-sm relative">
            <button
              onClick={() => setShowForgotPassword(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
            <h3 className="text-xl font-semibold mb-4">Reset Password</h3>
            <form onSubmit={handleResetPassword} className="flex flex-col gap-4">
              <input
                type="email"
                placeholder="Enter your email"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#E1E9EF]"
                required
              />
              <button
                type="submit"
                className="bg-[#234869] text-white p-3 rounded-lg font-medium hover:bg-[#E1E9EF] hover:text-[#234869] transition-colors disabled:opacity-50"
                disabled={isResetting}
              >
                {isResetting ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
