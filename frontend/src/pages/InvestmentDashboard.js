import React, { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { 
  Heading, Flex, Divider, Card, View, Loader, Table, 
  TableHead, TableRow, TableCell, TableBody, Button, 
  Text, Badge, ScrollView 
} from '@aws-amplify/ui-react';
import { getItems, getInvestmentAccounts, getInvestmentHoldings } from '../graphql/queries';
import Currency from '../components/Currency';

function InvestmentDashboard() {
  const [institutions, setInstitutions] = useState([]);
  const [investmentAccounts, setInvestmentAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [holdingsLoading, setHoldingsLoading] = useState(false);
  const client = generateClient();

  useEffect(() => {
    fetchInvestmentData();
  }, []);

  async function fetchInvestmentData() {
    setLoading(true);
    try {
      // 1. Fetch all institutions (items)
      const itemsResponse = await client.graphql({
        query: getItems
      });
      const items = itemsResponse.data.getItems.items;
      setInstitutions(items);
      
      // 2. Fetch investment accounts for each institution
      const allAccounts = [];
      for (const item of items) {
        try {
          const accountsResponse = await client.graphql({
            query: getInvestmentAccounts,
            variables: { id: item.item_id }
          });
          
          // Add institution name to each account for display
          if (accountsResponse.data.getInvestmentAccounts) {
            const accounts = accountsResponse.data.getInvestmentAccounts.map(account => ({
              ...account,
              institution_name: item.institution_name,
              item_id: item.item_id
            }));
            
            allAccounts.push(...accounts);
          }
        } catch (error) {
          console.error(`Error fetching accounts for item ${item.item_id}:`, error);
        }
      }
      
      setInvestmentAccounts(allAccounts);
      
      // If we have accounts, select the first one and fetch its holdings
      if (allAccounts.length > 0) {
        setSelectedAccount(allAccounts[0]);
        fetchHoldings(allAccounts[0].account_id);
      }
    } catch (err) {
      console.error('Error fetching investment data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function fetchHoldings(accountId) {
    if (!accountId) return;
    
    setHoldingsLoading(true);
    try {
      const holdingsResponse = await client.graphql({
        query: getInvestmentHoldings,
        variables: { accountId }
      });
      
      setHoldings(holdingsResponse.data.getInvestmentHoldings || []);
    } catch (err) {
      console.error('Error fetching investment holdings:', err);
      setHoldings([]);
    } finally {
      setHoldingsLoading(false);
    }
  }

  const selectAccount = (account) => {
    setSelectedAccount(account);
    fetchHoldings(account.account_id);
  };

  return (
    <View>
      <Heading level={2}>Investment Dashboard</Heading>
      <Divider orientation="horizontal" marginBottom="1rem" />
      
      {loading ? (
        <Flex direction="column" alignItems="center" justifyContent="center" padding="3rem">
          <Loader size="large" />
        </Flex>
      ) : (
        <Flex direction="column" gap="1.5rem">
          {/* Summary Card */}
          <Card padding="1.5rem">
            <Heading level={4}>Investment Summary</Heading>
            <Flex justifyContent="space-between" marginTop="1rem">
              <Card variation="outlined" padding="1rem" width="30%">
                <Heading level={6}>Total Portfolio Value</Heading>
                <Currency 
                  amount={investmentAccounts.reduce((sum, account) => {
                    return sum + parseFloat(account.balances?.current || 0);
                  }, 0)} 
                  currency="USD" 
                />
              </Card>
              
              <Card variation="outlined" padding="1rem" width="30%">
                <Heading level={6}>Accounts</Heading>
                {investmentAccounts.length}
              </Card>
              
              <Card variation="outlined" padding="1rem" width="30%">
                <Heading level={6}>Institutions</Heading>
                {institutions.length}
              </Card>
            </Flex>
          </Card>
          
          {/* Accounts and Holdings Section */}
          <Flex gap="1.5rem" className="investment-dashboard-flex">
            {/* Accounts List */}
            <Card padding="1.5rem" width="35%">
              <Heading level={4}>Investment Accounts</Heading>
              <ScrollView height="400px" marginTop="1rem">
                {investmentAccounts.length > 0 ? (
                  investmentAccounts.map((account) => (
                    <Card 
                      key={account.account_id}
                      variation={selectedAccount?.account_id === account.account_id ? "filled" : "outlined"} 
                      padding="1rem"
                      marginBottom="0.5rem"
                      onClick={() => selectAccount(account)}
                      className="clickable-card"
                    >
                      <Flex direction="column" gap="0.5rem">
                        <Flex justifyContent="space-between" alignItems="flex-start">
                          <Text fontWeight="bold">{account.name}</Text>
                          <Badge variation="info">{account.subtype || account.type}</Badge>
                        </Flex>
                        <Text fontSize="0.9rem" color="grey">{account.institution_name}</Text>
                        <Text fontWeight="bold">
                          <Currency 
                            amount={account.balances?.current} 
                            currency={account.balances?.iso_currency_code} 
                          />
                        </Text>
                      </Flex>
                    </Card>
                  ))
                ) : (
                  <Card variation="outlined" padding="1rem">
                    <Text>No investment accounts found. Connect accounts from the home page.</Text>
                  </Card>
                )}
              </ScrollView>
            </Card>
            
            {/* Holdings Table */}
            <Card padding="1.5rem" width="65%">
              <Flex justifyContent="space-between" alignItems="center">
                <Heading level={4}>
                  {selectedAccount ? `Holdings: ${selectedAccount.name}` : 'Select an Account'}
                </Heading>
                {selectedAccount && (
                  <Button 
                    size="small" 
                    onClick={() => fetchHoldings(selectedAccount.account_id)}
                    isLoading={holdingsLoading}
                  >
                    Refresh
                  </Button>
                )}
              </Flex>
              
              {holdingsLoading ? (
                <Flex justifyContent="center" padding="2rem">
                  <Loader />
                </Flex>
              ) : (
                <Table highlightOnHover={true} variation="striped" marginTop="1rem">
                  <TableHead>
                    <TableRow>
                      <TableCell as="th">Security</TableCell>
                      <TableCell as="th">Ticker</TableCell>
                      <TableCell as="th">Quantity</TableCell>
                      <TableCell as="th">Price</TableCell>
                      <TableCell as="th">Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {holdings.length > 0 ? (
                      holdings.map((holding) => (
                        <TableRow key={`${holding.account_id}-${holding.security_id}`}>
                          <TableCell>{holding.security?.name || 'Unknown'}</TableCell>
                          <TableCell>{holding.security?.ticker_symbol || '-'}</TableCell>
                          <TableCell>{holding.quantity}</TableCell>
                          <TableCell>
                            <Currency 
                              amount={holding.security?.close_price} 
                              currency={holding.security?.iso_currency_code} 
                            />
                          </TableCell>
                          <TableCell>
                            <Currency 
                              amount={holding.institution_value || parseFloat(holding.quantity) * parseFloat(holding.security?.close_price || 0)} 
                              currency={holding.iso_currency_code} 
                            />
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan="5">
                          {selectedAccount ? 'No holdings data available for this account.' : 'Select an account to view holdings.'}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              )}
            </Card>
          </Flex>
        </Flex>
      )}
    </View>
  );
}

export default InvestmentDashboard;
