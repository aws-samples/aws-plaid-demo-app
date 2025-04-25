import { useState } from 'react';
import { Button, Flex, Text, Alert } from '@aws-amplify/ui-react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { disconnectItem } from '../graphql/queries';
import { useNavigate } from 'react-router-dom';

const logger = new ConsoleLogger("Disconnect");

export default function Disconnect({ id, institutionName }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const client = generateClient();

  const handleDisconnect = async () => {
    if (window.confirm(`Are you sure you want to disconnect from ${institutionName}? This will remove all your accounts and data from this institution.`)) {
      setIsLoading(true);
      setError(null);
      
      try {
        await client.graphql({
          query: disconnectItem,
          variables: { id }
        });
        
        // Redirect to home page after successful disconnect
        navigate('/');
      } catch (err) {
        logger.error('Failed to disconnect item', err);
        setError('Failed to disconnect. Please try again later.');
        setIsLoading(false);
      }
    }
  };

  return (
    <Flex direction="column" gap="0.5rem">
      {error && (
        <Alert variation="error">
          {error}
        </Alert>
      )}
      <Button
        variation="destructive"
        size="small"
        onClick={handleDisconnect}
        isLoading={isLoading}
      >
        Disconnect Institution
      </Button>
      <Text fontSize="small" color="grey">
        This will remove all your account data from this institution.
      </Text>
    </Flex>
  );
}