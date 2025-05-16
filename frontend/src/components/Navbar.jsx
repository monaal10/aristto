import React, { useState } from 'react';
import { IconButton, Menu, MenuItem, Button } from '@mui/material';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import MenuIcon from '@mui/icons-material/Menu';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'context/authContext.jsx';

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [companyAnchorEl, setCompanyAnchorEl] = useState(null);

  // Menu handlers
  const handleMenuOpen = (event) => setMenuAnchorEl(event.currentTarget);
  const handleMenuClose = () => setMenuAnchorEl(null);

  // Company dropdown handlers
  const handleCompanyMenuOpen = (event) => setCompanyAnchorEl(event.currentTarget);
  const handleCompanyMenuClose = () => setCompanyAnchorEl(null);

  // Navigation handlers
  const handleLogin = () => navigate('/login');
  const handleHome = () => navigate('/');
  const goToLibrary = () => navigate('/library');
  const goToProfilePage = () => navigate('/profile');
  const goToBlogs = () => {
    handleCompanyMenuClose();
    navigate('/blogs');
  };
  const goToAbout = () => {
    handleCompanyMenuClose();
    navigate('/about');
  };
  const goToTeam = () => {
    handleCompanyMenuClose();
    navigate('/team');
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    navigate('/login', { replace: true });
  };

  const menuStyles = {
    "& .MuiPaper-root": {
      backgroundColor: '#EFE9E4',
      borderRadius: '15px',
      marginTop: '8px',
      minWidth: '150px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      border: '1px solid rgba(179, 153, 132, 0.2)',
    },
    "& .MuiMenuItem-root": {
      color: '#836F60',
      fontSize: '0.95rem',
      padding: '10px 20px',
      '&:hover': {
        backgroundColor: 'rgba(179, 153, 132, 0.1)',
      },
      '&:not(:last-child)': {
        borderBottom: '1px solid rgba(179, 153, 132, 0.1)',
      },
    },
  };


  return (
    <div className="bg-[#234869] rounded-full w-[90vw]  shadow-none h-16 flex justify-between items-center mx-auto p-4 my-4">
      <img
        onClick={handleHome}
        src="/WhiteLogo.png"
        alt="Logo"
        className="h-8 md:h-12 cursor-pointer"
      />

      <div className="flex items-center space-x-4 px-8">
        {isAuthenticated ? (
          <>
            <div className="relative group">
              <IconButton
                className="text-white hover:text-blue-300"
                onClick={goToLibrary}
              >
                <BookmarkBorderIcon fontSize="medium" className="text-white md:scale-125" />
              </IconButton>
              <span
                className="absolute left-1/2 -translate-x-1/2 -bottom-8 bg-black text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    Library
              </span>
            </div>


            {/* Uncomment to show profile button
            <IconButton
              className="text-white hover:text-blue-300"
              onClick={goToProfilePage}
            >
              <PersonOutlineIcon fontSize="medium" className="text-white md:scale-125" />
            </IconButton>*/}

            <IconButton
              className="text-white hover:text-blue-300"
              onClick={handleMenuOpen}
            >
              <MenuIcon fontSize="medium" className="text-white md:scale-125" />
            </IconButton>

            <Menu
              anchorEl={menuAnchorEl}
              open={Boolean(menuAnchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </>
        ) : (
          <div className="flex items-center space-x-4">
            {/*<Button
              endIcon={<KeyboardArrowDownIcon />}
              onClick={handleCompanyMenuOpen}
              className="text-white hover:text-[#EFE9E4] transition-colors font-medium normal-case"
              sx={{ color: 'white' }}
            >
              Company
            </Button>*/}
            <Menu
              anchorEl={companyAnchorEl}
              open={Boolean(companyAnchorEl)}
              onClose={handleCompanyMenuClose}
              sx={menuStyles}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem onClick={goToAbout}>About</MenuItem>
              <MenuItem onClick={goToTeam}>Team</MenuItem>
              <MenuItem onClick={goToBlogs}>Blogs</MenuItem>
            </Menu>

            <Button
              variant="text"
              onClick={handleLogin}
              sx={{ color: '#FFFFFF' }}
              className="text-[#836F60] font-bold rounded-full px-4 py-1 mx-2 font-['Iowan_Old_Style']"
            >
              Login
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
