import React, { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Eye, EyeOff } from 'lucide-react';
import apiClient from 'config/apiConfig';


const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    user_type: '',
    acquisition_channel: '',
    other_channel: '',
  });
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [isVerificationSent, setIsVerificationSent] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validatePassword = (password) => {
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!validatePassword(formData.password)) {
      setErrorMessage('Password must have at least 8 characters, an uppercase letter, a lowercase letter, a number, and a special character.');
      toast.error('Password does not meet the requirements');
      return;
    }

    if (!formData.user_type) {
      setErrorMessage('Please select what you do');
      toast.error('Please select what you do');
      return;
    }

    if (!formData.acquisition_channel) {
      setErrorMessage('Please tell us how you found us');
      toast.error('Please tell us how you found us');
      return;
    }

    if (formData.acquisition_channel === 'Other' && !formData.other_channel) {
      setErrorMessage('Please specify how you found us');
      toast.error('Please specify how you found us');
      return;
    }

    // Prepare data to send to backend
    const dataToSend = {
      ...formData,
      // If "Other" is selected, use the text from other_channel
      acquisition_channel: formData.acquisition_channel === 'Other' ? formData.other_channel : formData.acquisition_channel
    };

    // Remove other_channel as it's not needed in the API
    delete dataToSend.other_channel;

    try {
      const signupResponse = await apiClient.post('/user/create', dataToSend);

      if (signupResponse.status === 201) {
        setIsVerificationSent(true);
        setSuccessMessage('Please check your email to verify your account before logging in.');
        toast.success('Account created! Please check your email to verify your account.');
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Failed to create account';
      setErrorMessage(message);
      toast.error(message);
    }
  };
  if (isVerificationSent) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-50 px-4 py-6"
           style={{ background: 'linear-gradient(to bottom, #FFFFFF 23%, #E1E9EF 100%)' }}>
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <img src="/WhiteLogo.png" alt="Arissto Icon" className="mx-auto mb-6 w-40 h-auto" />
          <h2 className="text-2xl font-semibold mb-4">Verify Your Email</h2>
          <p className="text-gray-600 mb-6">
            We&#39;ve sent a verification link to {formData.email}. Please check your email and click the link to verify your account.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Once verified, you can <Link to="/login" className="text-[#234869] hover:underline">log in</Link> to your account.
          </p>
          <button
            onClick={() => setIsVerificationSent(false)}
            className="text-[#234869] hover:underline"
          >
            Back to Sign Up
          </button>
        </div>
      </div>
    );
  }

  // Label component with required asterisk
  const LabelWithAsterisk = ({ text }) => (
    <label className="text-sm font-medium text-gray-700 mb-1">
      {text} <span className="text-red-500">*</span>
    </label>
  );

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50 px-4 py-6"
         style={{ background: 'linear-gradient(to bottom, #FFFFFF 23%, #E1E9EF 100%)' }}>
      <ToastContainer />
      <div className="flex flex-col md:flex-row w-full max-w-4xl rounded-lg overflow-hidden shadow-lg">
        {/* Left Panel - Signup Form */}
        <div className="w-full md:w-1/2 bg-white p-6 md:p-8 flex flex-col justify-center">
          <h2 className="text-2xl font-semibold mb-6">Create Your Account</h2>

          {errorMessage && <p className="text-red-500 mb-4">{errorMessage}</p>}
          {successMessage && <p className="text-green-500 mb-4">{successMessage}</p>}

          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="flex flex-col">
              <LabelWithAsterisk text="First Name" />
              <input
                type="text"
                name="first_name"
                placeholder="First Name"
                value={formData.first_name}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                required
              />
            </div>

            <div className="flex flex-col">
              <LabelWithAsterisk text="Last Name" />
              <input
                type="text"
                name="last_name"
                placeholder="Last Name"
                value={formData.last_name}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                required
              />
            </div>

            <div className="flex flex-col">
              <LabelWithAsterisk text="Email" />
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                required
              />
            </div>

            <div className="flex flex-col">
              <LabelWithAsterisk text="What do you do?" />
              <select
                name="user_type"
                value={formData.user_type}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                required
              >
                <option value="" disabled>Select your role</option>
                <option value="Undergraduate Student">Undergraduate Student</option>
                <option value="Grad student">Grad student</option>
                <option value="Phd">Phd</option>
                <option value="Postdoc">Postdoc</option>
                <option value="Professor">Professor</option>
                <option value="Professional">Professional</option>
              </select>
            </div>

            <div className="flex flex-col">
              <LabelWithAsterisk text="How did you find us?" />
              <select
                name="acquisition_channel"
                value={formData.acquisition_channel}
                onChange={handleChange}
                className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                required
              >
                <option value="" disabled>Select an option</option>
                <option value="Google Search">Google Search</option>
                <option value="Linkedin">LinkedIn</option>
                <option value="Reddit">Reddit</option>
                <option value="X">X</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {formData.acquisition_channel === 'Other' && (
              <div className="flex flex-col">
                <LabelWithAsterisk text="Please specify" />
                <input
                  type="text"
                  name="other_channel"
                  placeholder="Please specify"
                  value={formData.other_channel}
                  onChange={handleChange}
                  className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869]"
                  required
                />
              </div>
            )}

            <div className="flex flex-col">
              <LabelWithAsterisk text="Password" />
              <div className="relative">
                <input
                  type={passwordVisible ? "text" : "password"}
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  className="p-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#234869] w-full"
                  required
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 text-gray-500"
                  onClick={() => setPasswordVisible(!passwordVisible)}
                >
                  {passwordVisible ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Must contain at least 8 characters, an uppercase letter, a number, and a special character.
              </p>
            </div>

            <button type="submit" className="bg-[#234869] text-white p-3 rounded-lg font-medium hover:bg-[#234869] transition-colors mt-2">
              Sign Up
            </button>
          </form>
        </div>

        {/* Right Panel - Welcome Message */}
        <div className="w-full md:w-1/2 bg-[#234869] p-6 md:p-8 flex flex-col justify-center items-start text-white relative">
          <img src="/WhiteLogo.png" alt="Arissto Icon" className="mb-4 w-40 h-auto"  />
          <h3 className="text-3xl font-semibold mb-4">Already a Member?</h3>
          <p className="mb-8 text-teal-50">Log in to your account to continue your journey!</p>
          <Link to="/login" className="px-6 py-2 rounded-lg border-2 border-white text-white font-medium hover:bg-white hover:text-[#234869] transition-colors flex items-center gap-2">
            Log In
            <ChevronRight size={20} />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
