import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuthenticator, Button, Heading, View, Flex, Text } from '@aws-amplify/ui-react';

export default function Layout() {
  const { route, signOut, user } = useAuthenticator((context) => [
    context.route,
    context.signOut,
    context.user
  ]);
  const navigate = useNavigate();

  function logOut() {
    signOut();
    navigate('/login');
  }
  
  return (
    <>
      <nav>
        <div className="nav-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 13.125C3 12.5727 3.44772 12.125 4 12.125H6C6.55228 12.125 7 12.5727 7 13.125V20C7 20.5523 6.55228 21 6 21H4C3.44772 21 3 20.5523 3 20V13.125Z" fill="currentColor"/>
            <path d="M10 8.125C10 7.57272 10.4477 7.125 11 7.125H13C13.5523 7.125 14 7.57272 14 8.125V20C14 20.5523 13.5523 21 13 21H11C10.4477 21 10 20.5523 10 20V8.125Z" fill="currentColor"/>
            <path d="M17 3.125C17 2.57272 17.4477 2.125 18 2.125H20C20.5523 2.125 21 2.57272 21 3.125V20C21 20.5523 20.5523 21 20 21H18C17.4477 21 17 20.5523 17 20V3.125Z" fill="currentColor"/>
          </svg>
          <span>Passive Analytics</span>
        </div>
        <div className="nav-links">
          <Button 
            size="small" 
            onClick={() => navigate('/')}
            variation="link"
          >
            Dashboard
          </Button>
          {route === 'authenticated' && (
            <Button 
              size="small" 
              onClick={() => logOut()}
              variation="link"
            >
              Sign Out
            </Button>
          )}
          {route !== 'authenticated' && (
            <Button 
              size="small" 
              onClick={() => navigate('/login')}
              variation="primary"
            >
              Sign In
            </Button>
          )}
        </div>
      </nav>
      
      {route === 'authenticated' ? (
        <Flex direction="column" alignItems="flex-start" marginBottom="1.5rem">
          <Heading level={3} className="app-title">
            Financial Dashboard
          </Heading>
          <Text className="welcome-text">
            Welcome back, {user.signInDetails?.loginId}. Here's a snapshot of your investments.
          </Text>
        </Flex>
      ) : (
        <Flex direction="column" alignItems="center" marginY="2rem">
          <Heading level={3}>
            Make smarter investment decisions with Passive Analytics
          </Heading>
          <Text marginTop="1rem" color="var(--color-text-secondary)">
            Please sign in to access your personalized financial dashboard.
          </Text>
        </Flex>
      )}

      <Outlet />
    </>
  );
}
