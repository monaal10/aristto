import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from '../components/Navbar';

const MainLayout = () => {
  return (
    <Box sx={{
      background: 'linear-gradient(to bottom, #FFFFFF 0%, #E1E9EF 100%)',
      minHeight: '100vh',
      margin: 0,
      padding: 0,
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Navbar />
      <div style={{
        width: '100%',
        padding: 0,
        margin: 0,

      }}>
        <Outlet />
      </div>
    </Box>
  );
};

export default MainLayout;
