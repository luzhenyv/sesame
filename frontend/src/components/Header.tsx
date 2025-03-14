import React from 'react';
import styled from 'styled-components';
import { Link, useLocation } from 'react-router-dom';

const HeaderContainer = styled.header`
  background-color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;

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

  return (
    <HeaderContainer>
      <Link to="/" style={{ textDecoration: 'none' }}>
        <Logo>Health Monitor</Logo>
      </Link>
      <Nav>
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          Home
        </Link>
        <Link to="/family" className={location.pathname === '/family' ? 'active' : ''}>
          Family
        </Link>
        <Link to="/profile" className={location.pathname === '/profile' ? 'active' : ''}>
          Profile
        </Link>
      </Nav>
    </HeaderContainer>
  );
};

export default Header; 