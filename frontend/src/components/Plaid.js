import { useState, useEffect } from 'react';
import { get, post } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Button, Flex, Text, Card, Link } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new ConsoleLogger("Plaid");
logger.LOG_LEVEL = "DEBUG"; // Ensure verbose logging

const apiName = "plaidapi";

export default function Plaid({ refreshAccounts }) {
  const [connecting, setConnecting] = useState(false);
  const [token, setToken] = useState(null);
  const [error, setError] = useState(null);
  const [linkStatus, setLinkStatus] = useState("idle"); // idle, getting-token, token-ready, success, error

  const handleGetToken = async () => {
    setConnecting(true);
    setError(null);
    setLinkStatus("getting-token");
    
    try {
      logger.debug('Getting Plaid link token...');
      
      // Log the API configuration for debugging
      console.log('API config:', apiName);
      
      const response = await get({
        apiName,
        path: '/v1/tokens'
      }).response;
      
      // Log the full response for debugging
      console.log('Token response status:', response.statusCode);
      
      const { body } = response;
      const data = await body.json();
      
      console.log('GET /v1/tokens response:', data);
      logger.debug('GET /v1/tokens response:', data);
      
      if (data && data.link_token) {
        setToken(data.link_token);
        setLinkStatus("token-ready");
        console.log('Received link token:', data.link_token);
      } else {
        setError("Invalid response from server. Missing link token.");
        setLinkStatus("error");
        console.error('Invalid token response:', data);
      }
    } catch (err) {
      console.error('Error getting Plaid token:', err);
      logger.error('Unable to create link token:', err);
      setError("Failed to get link token. Check console for details.");
      setLinkStatus("error");
    }
  };

  const handleSuccess = async (public_token, metadata) => {
    try {
      logger.debug('Plaid link success, exchanging public token...');
      console.log('Public token received:', public_token);
      console.log('Metadata:', metadata);
      
      setLinkStatus("exchanging-token");
      
      // Exchange the public token for an access token
      const response = await post({
        apiName,
        path: '/v1/tokens',
        options: {
          body: {
            public_token,
            metadata
          },
        },
      }).response;
      
      console.log('Token exchange response status:', response.statusCode);
      
      const { body } = response;
      let data;
      try {
        data = await body.json();
      } catch (e) {
        // If it's not JSON, try getting text
        data = await body.text();
      }
      
      logger.debug('POST /v1/tokens response:', data);
      console.log('POST /v1/tokens response:', data);
      
      // Reset the token to null so PlaidLink component is removed
      setToken(null);
      setLinkStatus("success");
      
      // Refresh the accounts list with the newly added institution
      console.log('Refreshing accounts...');
      if (refreshAccounts) {
        setTimeout(() => {
          refreshAccounts();
        }, 2000); // Small delay to allow backend to process
      }
      
      setConnecting(false);
    } catch (err) {
      console.error('Error exchanging token:', err);
      logger.error('Unable to exchange public token', err);
      setError("Failed to exchange token. Check console for details.");
      setLinkStatus("error");
      setConnecting(false);
    }
  };
  
  // Handle exit - user closed Plaid Link without connecting an account
  const handleExit = (err) => {
    console.log('Plaid Link exited', err);
    setConnecting(false);
    setToken(null); // Reset token
    
    if (err) {
      console.error('Plaid Link exit error:', err);
      setError(`Plaid Link error: ${err.error_message || 'Unknown error'}`);
      setLinkStatus("error");
    } else {
      setLinkStatus("idle");
    }
  };

  // Render status messages for debugging
  const renderStatus = () => {
    if (linkStatus === "success") {
      return (
        <Card variation="elevated" backgroundColor="rgba(0, 200, 83, 0.1)" padding="1rem" marginTop="1rem">
          <Text color="green">Successfully connected account! Refreshing data...</Text>
        </Card>
      );
    }
    
    if (error) {
      return (
        <Card variation="elevated" backgroundColor="rgba(255, 59, 48, 0.1)" padding="1rem" marginTop="1rem">
          <Text color="red" fontWeight="bold">Error</Text>
          <Text color="red">{error}</Text>
          <Text fontSize="0.9rem" marginTop="0.5rem">
            Check browser console for detailed logs. <br/>
            Make sure your backend API is configured correctly.
          </Text>
        </Card>
      );
    }
    
    return null;
  };

  return (
    <Flex direction="column" width="100%">
      <Flex alignItems="center" gap="1rem">
        <Button
          variation="primary"
          isLoading={connecting}
          onClick={handleGetToken}
          isDisabled={linkStatus === "token-ready"}
        >
          CONNECT WITH PLAID
        </Button>
        
        {linkStatus === "getting-token" && (
          <Text>Getting Plaid token...</Text>
        )}
      </Flex>
      
      {renderStatus()}
      
      {token ? (
        <PlaidLink
          token={token}
          onSuccess={handleSuccess}
          onExit={handleExit}
        />
      ) : null}
    </Flex>
  );
}
