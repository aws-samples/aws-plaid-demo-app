import React, { useState, useEffect } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { Container, Heading, Flex, Divider, Button } from '@aws-amplify/ui-react';
import Institutions from '../components/Institutions';
import Plaid from '../components/Plaid';
import { getItems } from '../graphql/queries';

function AccountManagement() {
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstitutions();
  }, []);

  async function fetchInstitutions() {
    setLoading(true);
    try {
      const itemData = await API.graphql(graphqlOperation(getItems));
      setInstitutions(itemData.data.getItems);
    } catch (err) {
      console.log('error fetching institutions:', err);
    }
    setLoading(false);
  }

  return (
    <Container>
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
    </Container>
  );
}

export default AccountManagement;
