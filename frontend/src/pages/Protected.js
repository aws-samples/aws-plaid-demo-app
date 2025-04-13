import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { View, Heading, Flex, Card, Text, Grid, Loader, Button } from '@aws-amplify/ui-react';
import { getItems as GetItems, getAccounts as GetAccounts } from '../graphql/queries';
import { useNavigate } from 'react-router-dom';
import Currency from '../components/Currency';

const logger = new ConsoleLogger("Protected");

export default function Protected() {
  const [items, setItems] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    institutions: 0,
    accounts: 0,
    investmentAccounts: 0,
    totalInvestments: 0
  });
  const client = generateClient();
  const navigate = useNavigate();

  const getItems = async () => {
    setLoading(true);
    try {
      const res = await client.graphql({
        query: GetItems
      });
      logger.info(res);
      const itemsData = res.data.getItems;
      setItems(itemsData);
      setStats(prev => ({ ...prev, institutions: itemsData.length }));
      
      // Fetch accounts for each institution
      await fetchAllAccounts(itemsData);
    } catch (err) {
      logger.error('unable to get items', err);
    }
    setLoading(false);
  }

  const fetchAllAccounts = async (institutions) => {
    const allAccounts = [];
    let investmentAccounts = 0;
    let totalInvestments = 0;
    
    try {
      for (const item of institutions) {
        const accountsResponse = await client.graphql({
          query: GetAccounts,
          variables: { id: item.id }
        });
        const itemAccounts = accountsResponse.data.getAccounts;
        allAccounts.push(...itemAccounts);
        
        // Count investment accounts and total balance
        itemAccounts.forEach(account => {
          if (account.type === 'investment') {
            investmentAccounts++;
            totalInvestments += parseFloat(account.balances.current || 0);
          }
        });
      }
      
      setAccounts(allAccounts);
      setStats({
        institutions: institutions.length,
        accounts: allAccounts.length,
        investmentAccounts,
        totalInvestments
      });
    } catch (err) {
      logger.error('unable to fetch accounts', err);
    }
  }

  useEffect(() => {
    getItems();
  }, []);

  if (loading) {
    return (
      <Flex direction="column" alignItems="center" justifyContent="center" height="200px">
        <Loader size="large" />
        <Text variation="tertiary" marginTop="1rem">Loading your financial data...</Text>
      </Flex>
    );
  }

  return (
    <Flex direction="column" gap="2rem">
      {/* Dashboard Overview Cards */}
      <Grid templateColumns={{ base: "1fr", medium: "1fr 1fr 1fr" }} gap="1rem">
        <Card padding="1.5rem" variation="elevated" className="dashboard-card">
          <Heading level={5}>Connected Accounts</Heading>
          <Flex alignItems="center" gap="1rem" marginTop="1rem">
            <Text fontSize="2rem" fontWeight="bold" className="stat-value">{stats.accounts}</Text>
            <Flex direction="column" fontSize="0.875rem">
              <Text className="stat-label">{stats.institutions} Financial Institutions</Text>
              <Text className="stat-label">{stats.investmentAccounts} Investment Accounts</Text>
            </Flex>
          </Flex>
          <Button 
            size="small" 
            onClick={() => navigate('/accounts')} 
            marginTop="1rem"
          >
            Manage Accounts
          </Button>
        </Card>

        <Card padding="1.5rem" variation="elevated" className="dashboard-card">
          <Heading level={5}>Total Investments</Heading>
          <Text fontSize="2rem" fontWeight="bold" marginTop="1rem" className="stat-value">
            <Currency amount={stats.totalInvestments} currency="USD" />
          </Text>
          <Button 
            size="small" 
            onClick={() => navigate('/analytics')} 
            marginTop="1rem"
          >
            View Analytics
          </Button>
        </Card>

        <Card padding="1.5rem" variation="elevated" className="dashboard-card">
          <Heading level={5}>Recent Transactions</Heading>
          <Text marginTop="1rem">View your transaction history across all accounts</Text>
          <Button 
            size="small" 
            onClick={() => navigate('/transactions')} 
            marginTop="1rem"
          >
            View Transactions
          </Button>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Card padding="1.5rem">
        <Heading level={4}>Quick Actions</Heading>
        <Flex gap="1rem" marginTop="1rem" wrap="wrap">
          <Button 
            onClick={() => navigate('/accounts')}
            variation="primary"
          >
            Add New Account
          </Button>
          <Button 
            onClick={() => navigate('/analytics')}
          >
            View Investment Analytics
          </Button>
        </Flex>
      </Card>
      
      {/* No accounts yet prompt */}
      {stats.accounts === 0 && (
        <Card padding="2rem" textAlign="center">
          <Heading level={4}>Get Started</Heading>
          <Text marginY="1rem">
            Connect your first financial account to start tracking your investments
          </Text>
          <Button 
            onClick={() => navigate('/accounts')}
            variation="primary"
          >
            Connect Account
          </Button>
        </Card>
      )}
    </Flex>
  );
}
