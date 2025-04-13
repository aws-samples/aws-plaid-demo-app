import React, { useState, useEffect } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { Container, Heading, Flex, Divider, Card, Text, Badge } from '@aws-amplify/ui-react';
import Currency from '../components/Currency';
import { getItems, getAccounts } from '../graphql/queries';

function AnalyticsDashboard() {
  const [institutions, setInstitutions] = useState([]);
  const [allAccounts, setAllAccounts] = useState([]);
  const [summary, setSummary] = useState({
    totalInvestments: 0,
    accountCount: 0,
    institutionCount: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstitutions();
  }, []);

  async function fetchInstitutions() {
    setLoading(true);
    try {
      const itemData = await API.graphql(graphqlOperation(getItems));
      const items = itemData.data.getItems;
      setInstitutions(items);
      setSummary(prev => ({ ...prev, institutionCount: items.length }));
      
      // Fetch all accounts for each institution
      const accounts = [];
      for (const item of items) {
        const accountData = await API.graphql(
          graphqlOperation(getAccounts, { id: item.id })
        );
        accounts.push(...accountData.data.getAccounts);
      }
      
      setAllAccounts(accounts);
      calculateSummary(accounts);
    } catch (err) {
      console.log('error fetching data:', err);
    }
    setLoading(false);
  }

  function calculateSummary(accounts) {
    // Basic investment summary calculations
    const totalBalance = accounts.reduce((sum, account) => {
      // Only include investment accounts in calculation
      if (account.type === 'investment') {
        return sum + parseFloat(account.balances.current);
      }
      return sum;
    }, 0);

    setSummary({
      totalInvestments: totalBalance,
      accountCount: accounts.length,
      institutionCount: institutions.length
    });
  }

  return (
    <Container>
      <Heading level={2}>Investment Analytics</Heading>
      <Divider orientation="horizontal" marginBottom="1rem" />
      
      {loading ? (
        <Text>Loading your financial data...</Text>
      ) : (
        <Flex direction="column" gap="1.5rem">
          <Card padding="1.5rem">
            <Heading level={4}>Portfolio Summary</Heading>
            <Flex direction="row" gap="2rem" wrap="wrap" marginTop="1rem">
              <Card variation="outlined" padding="1rem">
                <Heading level={6}>Total Investments</Heading>
                <Text fontSize="1.5rem">
                  <Currency amount={summary.totalInvestments} currency="USD" />
                </Text>
              </Card>
              
              <Card variation="outlined" padding="1rem">
                <Heading level={6}>Connected Accounts</Heading>
                <Text fontSize="1.5rem">{summary.accountCount}</Text>
              </Card>
              
              <Card variation="outlined" padding="1rem">
                <Heading level={6}>Financial Institutions</Heading>
                <Text fontSize="1.5rem">{summary.institutionCount}</Text>
              </Card>
            </Flex>
          </Card>
          
          <Card padding="1.5rem">
            <Heading level={4}>Your Investment Accounts</Heading>
            <Divider marginTop="0.5rem" marginBottom="1rem" />
            
            {allAccounts.length > 0 ? (
              <Flex direction="column" gap="1rem">
                {allAccounts
                  .filter(account => account.type === 'investment')
                  .map(account => (
                    <Card key={account.id} variation="outlined" padding="1rem">
                      <Flex justifyContent="space-between" alignItems="center">
                        <div>
                          <Text fontWeight="bold">{account.name}</Text>
                          <Text color="grey">
                            {institutions.find(i => i.id === account.item_id)?.name || 'Unknown'}
                          </Text>
                        </div>
                        <div>
                          <Text fontWeight="bold">
                            <Currency amount={account.balances.current} currency={account.balances.iso_currency_code} />
                          </Text>
                          <Badge variation="info">{account.subtype || 'Investment'}</Badge>
                        </div>
                      </Flex>
                    </Card>
                  ))}
              </Flex>
            ) : (
              <Text>No investment accounts found. Connect accounts to see data.</Text>
            )}
          </Card>
          
          <Card padding="1.5rem">
            <Heading level={4}>Coming Soon</Heading>
            <Text>Advanced investment analytics, portfolio performance, and asset allocation.</Text>
          </Card>
        </Flex>
      )}
    </Container>
  );
}

export default AnalyticsDashboard;
