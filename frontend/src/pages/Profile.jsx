import React from 'react';
import BackButton from 'components/BackButton.jsx'
import { useAuth } from 'context/AuthContext';
import apiClient from 'config/apiConfig.js'

const Profile = () => {
  const { user } = useAuth();
  const formData = {
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    password: '************',
    plan: user?.plan || 'free'
  };

  const handleManageSubscription = async () => {
    try {
      const response = await apiClient.post('/stripe/create-portal-session', {});

      // Redirect to the portal URL
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Error accessing billing portal:', error);
      // Add your error handling here
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="w-12 -ml-20 -mt-10">
        <BackButton />
      </div>
      <div className="mb-20">
        <h2 className="text-[#5D4037] text-3xl sm:text-5xl font-lato font-bold">Profile</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-x-8 gap-y-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Name fields side by side */}
          <div className="grid grid-cols-2 gap-4">
            {['first name', 'last name'].map((field, index) => (
              <div key={index}>
                <label className="block text-sm text-[#5D4037] uppercase tracking-wide mb-2">
                  {field}
                </label>
                <div className="w-52 p-3 bg-[#F8F5F0] rounded-[10px]">
                  {formData[field.replace(' ', '_')]}
                </div>
              </div>
            ))}
          </div>

          {/* Email and Password fields */}
          {['email', 'password'].map((field) => (
            <div key={field}>
              <label className="block text-sm text-[#5D4037] uppercase tracking-wide mb-2">
                {field}
              </label>
              <div className="w-72 p-3 bg-[#F8F5F0] rounded-[10px] text-left ">
                {formData[field]}
              </div>
            </div>
          ))}
          <div>
            <button
              onClick={() => {
                window.location.href = "https://billing.stripe.com/p/login/00g9E0da0cTYcmY7ss";
              }}
              className="px-6 py-2 bg-[#D7C9BF] text-[#5D4037] font-bold rounded-full hover:bg-[#B69B85] transition-colors"
            >
              Manage Subscription
            </button>

          </div>
        </div>

        <div className="space-y-6">
          <>

          </>
        </div>
      </div>
    </div>
  )
    ;
};

export default Profile;

