import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #1a1a1a;
  color: white;
  padding: 2rem;
  text-align: center;

  @media (max-width: 768px) {
    padding: 1rem;
    font-size: 0.875rem;
  }
`;

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <p>© 2024 Health Monitor. All rights reserved.</p>
    </FooterContainer>
  );
};

export default Footer; 