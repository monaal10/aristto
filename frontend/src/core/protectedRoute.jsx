import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from 'context/authContext';

const ProtectedRoute = ({ children, requireSubscription = false }) => {  // Changed default to false
  const { isAuthenticated, user, loading } = useAuth();
  const navigate = useNavigate();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) {
        navigate('/login');
      } else if (requireSubscription && user?.plan !== 'pro') {
        navigate('/pricing');
      }
      setChecked(true);
    }
  }, [isAuthenticated, user, loading, navigate, requireSubscription]);

  if (loading || !checked) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#B39984]"></div>
      </div>
    );
  }

  if (!isAuthenticated || (requireSubscription && user?.plan !== 'pro')) {
    return null;
  }

  return children;
};

export default ProtectedRoute;
