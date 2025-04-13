import React, { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { Heading, Flex, Divider, Button, View, Card, Text, Alert } from '@aws-amplify/ui-react';
import Institutions from '../components/Institutions';
import Plaid from '../components/Plaid';
import { getItems } from '../graphql/queries';

function AccountManagement() {
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const client = generateClient();

  useEffect(() => {
    fetchInstitutions();
  }, [refreshTrigger]);

  // Function to refresh institutions after Plaid connection
  const handleRefreshAccounts = () => {
    console.log("Refreshing accounts...");
    setRefreshTrigger(prev => prev + 1);
  };

  async function fetchInstitutions() {
    setLoading(true);
    setError(null);
    
    console.log("Fetching institutions...");
    
    try {
      const itemData = await client.graphql({
        query: getItems
      });
      
      console.log("Institutions response:", itemData);
      
      if (itemData.data && itemData.data.getItems) {
        setInstitutions(itemData.data.getItems);
        console.log("Institutions loaded:", itemData.data.getItems.length);
      } else {
        console.warn("Unexpected response format:", itemData);
        setError("Invalid response format when fetching institutions");
      }
    } catch (err) {
      console.error('Error fetching institutions:', err);
      setError("Failed to fetch institutions. See console for details.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View>
      <Heading level={2}>Manage Your Financial Accounts</Heading>
      <Divider orientation="horizontal" marginBottom="1rem" />
      
      {error && (
        <Alert
          variation="error"
          isDismissible={true}
          hasIcon={true}
          heading="Error"
          marginBottom="1rem"
        >
          {error}
        </Alert>
      )}
      
      <Flex direction="column" gap="1.5rem">
        <Card padding="1.5rem" variation="outlined">
          <Heading level={4}>Connect a New Account</Heading>
          <Text marginBottom="1rem">
            Link your investment accounts to enable analysis across all your investments.
          </Text>
          <Plaid refreshAccounts={handleRefreshAccounts} />
        </Card>
        
        <Card padding="1.5rem" variation="outlined">
          <Heading level={4}>Your Connected Accounts</Heading>
          <Institutions 
            institutions={institutions} 
            loading={loading}
            isManagementView={true} 
          />
          
          {!loading && institutions.length === 0 && (
            <Text marginTop="1rem">
              No financial institutions connected yet. Use the "Connect with Plaid" button above to link your first account.
            </Text>
          )}
          
          <Button 
            onClick={handleRefreshAccounts}
            variation="link"
            size="small"
            marginTop="1rem"
            isDisabled={loading}
          >
            Refresh List
          </Button>
        </Card>
      </Flex>
    </View>
  );
}

export default AccountManagement;
