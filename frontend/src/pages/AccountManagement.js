import React, { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { Heading, Flex, Divider, Button, View } from '@aws-amplify/ui-react';
import Institutions from '../components/Institutions';
import Plaid from '../components/Plaid';
import { getItems } from '../graphql/queries';

function AccountManagement() {
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const client = generateClient();

  useEffect(() => {
    fetchInstitutions();
  }, []);

  async function fetchInstitutions() {
    setLoading(true);
    try {
      const itemData = await client.graphql({
        query: getItems
      });
      setInstitutions(itemData.data.getItems);
    } catch (err) {
      console.log('error fetching institutions:', err);
    }
    setLoading(false);
  }

  return (
    <View>
      <Heading level={2}>Manage Your Financial Accounts</Heading>
      <Divider orientation="horizontal" marginBottom="1rem" />
      
      <Flex direction="column" gap="1.5rem">
        <Plaid refreshAccounts={fetchInstitutions} />
        <Institutions 
          institutions={institutions} 
          loading={loading}
          isManagementView={true} 
        />
      </Flex>
    </View>
  );
}

export default AccountManagement;
