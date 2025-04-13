import React, { useState, useEffect } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { Container, Heading, Flex, Divider, Select, Button } from '@aws-amplify/ui-react';
import Transactions from '../components/Transactions';
import { getItems, getAccounts } from '../graphql/queries';

function TransactionsDashboard() {
  const [institutions, setInstitutions] = useState([]);
  const [selectedInstitution, setSelectedInstitution] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [accountMap, setAccountMap] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstitutions();
  }, []);

  useEffect(() => {
    if (selectedInstitution) {
      fetchAccounts(selectedInstitution);
    }
  }, [selectedInstitution]);

  async function fetchInstitutions() {
    setLoading(true);
    try {
      const itemData = await API.graphql(graphqlOperation(getItems));
      const items = itemData.data.getItems;
      setInstitutions(items);
      if (items.length > 0) {
        setSelectedInstitution(items[0].id);
      }
    } catch (err) {
      console.log('error fetching institutions:', err);
    }
    setLoading(false);
  }

  async function fetchAccounts(institutionId) {
    setLoading(true);
    try {
      const accountData = await API.graphql(
        graphqlOperation(getAccounts, { id: institutionId })
      );
      const accountsList = accountData.data.getAccounts;
      setAccounts(accountsList);

      // Create account map for transaction component
      const newAccountMap = {};
      accountsList.forEach(account => {
        newAccountMap[account.id] = account;
      });
      setAccountMap(newAccountMap);
    } catch (err) {
      console.log('error fetching accounts:', err);
    }
    setLoading(false);
  }

  return (
    <Container>
      <Heading level={2}>All Transactions</Heading>
      <Divider orientation="horizontal" marginBottom="1rem" />
      
      <Flex direction="column" gap="1.5rem">
        <Select
          label="Select Institution"
          value={selectedInstitution}
          onChange={e => setSelectedInstitution(e.target.value)}
          disabled={loading || institutions.length === 0}
        >
          {institutions.map(institution => (
            <option key={institution.id} value={institution.id}>
              {institution.name}
            </option>
          ))}
        </Select>

        {selectedInstitution && (
          <Transactions accountMap={accountMap} institutionId={selectedInstitution} />
        )}
      </Flex>
    </Container>
  );
}

export default TransactionsDashboard;
