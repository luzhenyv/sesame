import React from 'react';
import styled from 'styled-components';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Box,
} from '@mui/material';
import { useAuth } from '../context/AuthContext.tsx';

const HeaderContainer = styled.header`
  background-color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  position: sticky;
  top: 0;
  z-index: 1000;

  @media (max-width: 768px) {
    padding: 1rem;
  }
`;

const Logo = styled.h1`
  font-size: 1.5rem;
  color: #1a1a1a;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.25rem;
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 2rem;
  align-items: center;

  a {
    color: #4a4a4a;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
    
    &:hover {
      color: #007AFF;
    }

    &.active {
      color: #007AFF;
      font-weight: 600;
    }
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
    margin-top: 0.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }
`;

const Header: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
    handleClose();
  };

  return (
    <HeaderContainer>
      <Link to="/" style={{ textDecoration: 'none' }}>
        <Logo>Health Monitor</Logo>
      </Link>
      <Nav>
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          Home
        </Link>
        
        {isAuthenticated ? (
          <>
            <Link to="/family" className={location.pathname === '/family' ? 'active' : ''}>
              Family
            </Link>
            <Link to="/profile" className={location.pathname === '/profile' ? 'active' : ''}>
              Profile
            </Link>
            <Box>
              <IconButton
                onClick={handleMenu}
                size="small"
                sx={{ ml: 2 }}
                aria-controls={Boolean(anchorEl) ? 'account-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={Boolean(anchorEl) ? 'true' : undefined}
              >
                <Avatar sx={{ width: 32, height: 32 }}>
                  {user?.name?.[0] || 'U'}
                </Avatar>
              </IconButton>
              <Menu
                id="account-menu"
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                onClick={handleClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem onClick={() => { navigate('/profile'); handleClose(); }}>
                  Profile
                </MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </Box>
          </>
        ) : (
          <>
            <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>
              Login
            </Link>
          </>
        )}
      </Nav>
    </HeaderContainer>
  );
};

export default Header; 