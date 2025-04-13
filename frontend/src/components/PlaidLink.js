import { useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';

export default function PlaidLink({ token, onSuccess, onExit }) {
  // Configure Plaid Link with additional options for better UX and testing
  const config = {
    token,
    onSuccess,
    onExit,
    // Optional: Add more configuration for testing/debugging
    receivedRedirectUri: window.location.href,
    // Additional options to help with testing
    env: 'sandbox', // Use sandbox mode explicitly
  };
  
  const { open, ready, error } = usePlaidLink(config);

  // Log component lifecycle and errors
  useEffect(() => {
    console.log('PlaidLink initialized with token:', token);
    console.log('PlaidLink ready state:', ready);
    
    if (error) {
      console.error('PlaidLink initialization error:', error);
    }
  }, [token, ready, error]);

  // Open Plaid Link once token is available and component is ready
  useEffect(() => {
    if (token && ready) {
      console.log('Opening Plaid Link...');
      try {
        open(); 
      } catch (err) {
        console.error('Error opening Plaid Link:', err);
      }
    }
  }, [token, ready, open]);

  return <div />; // Component doesn't render anything visible
}
