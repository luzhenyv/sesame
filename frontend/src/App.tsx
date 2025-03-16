import React from 'react';
import Layout from './components/Layout';

interface AppProps {
  children?: React.ReactNode;
}

const App: React.FC<AppProps> = ({ children }) => {
  return (
    <Layout>
      {children}
    </Layout>
  );
};

export default App; 