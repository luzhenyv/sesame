import React from 'react';
import Header from './Header.tsx';
import Footer from './Footer.tsx';
import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
`;

const MainContent = styled.main`
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Container>
      <Header />
      <MainContent>
        {children}
      </MainContent>
      <Footer />
    </Container>
  );
};

export default Layout; 