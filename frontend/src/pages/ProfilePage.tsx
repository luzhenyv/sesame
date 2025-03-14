import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  color: #333;
  font-family: 'Roboto', sans-serif;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const ProfilePage: React.FC = () => {
  return (
    <Container>
      <MainContent>
        <h1>Profile Page</h1>
        <p>This page is under construction...</p>
      </MainContent>
    </Container>
  );
};

export default ProfilePage; 