import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader, View, Button, Flex, Heading, Text } from '@aws-amplify/ui-react';
import Transaction from './Transaction';
import { getTransactions as GetTransactions } from '../graphql/queries';

const logger = new ConsoleLogger("Transactions");

export default function Transactions({ institutionId, accountMap = {} }) {

  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [nextToken, setNextToken] = useState(null);
  const [hasMorePages, setHasMorePages] = useState(false);

  const client = generateClient();

  const getTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId }
      });
      
      if (res.data && res.data.getTransactions) {
        setTransactions(res.data.getTransactions.transactions || []);
        if (res.data.getTransactions.cursor) {
          setHasMorePages(true);
          setNextToken(res.data.getTransactions.cursor);
        } else {
          setHasMorePages(false);
        }
      } else {
        setTransactions([]);
        setHasMorePages(false);
      }
      
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setError('Failed to load transactions. Please try again later.');
      logger.error('unable to get transactions', err);
    }
  }

  const handleLoadMore = async () => {
    try {
      setError(null);
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId, cursor: nextToken }
      });
      
      if (res.data && res.data.getTransactions) {
        if (res.data.getTransactions.cursor) {
          setNextToken(res.data.getTransactions.cursor);
          setHasMorePages(true);
        }
        else {
          setHasMorePages(false);
        }
        
        if (res.data.getTransactions.transactions && res.data.getTransactions.transactions.length > 0) {
          setTransactions([...transactions, ...res.data.getTransactions.transactions]);
        }
      }
    } catch (err) {
      setError('Failed to load more transactions.');
      logger.error('unable to get transactions', err);
    }
  }

  useEffect(() => {
    if (institutionId) {
      getTransactions();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [institutionId]);

  return (
    <View>
      {error ? (
        <Flex direction="column" alignItems="center" padding="2rem" gap="1rem">
          <Heading level={5} color="red">{error}</Heading>
          <Button onClick={getTransactions} variation="primary" size="small">
            Try Again
          </Button>
        </Flex>
      ) : (
        <>
          <Table highlightOnHover={true} variation="striped">
            <TableHead>
              <TableRow>
                <TableCell as="th">Name</TableCell>
                <TableCell as="th">Amount</TableCell>
                <TableCell as="th">Date</TableCell>
                <TableCell as="th">Account</TableCell>
                <TableCell as="th">Payment Channel</TableCell>
                <TableCell as="th">Transaction Type</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan="6">
                    <Flex justifyContent="center" padding="2rem">
                      <Loader size="large" />
                    </Flex>
                  </TableCell>
                </TableRow>
              ) : (
                transactions.length > 0 ? (
                  transactions.map((transaction) => {
                    return <Transaction 
                      key={transaction.transaction_id} 
                      transaction={transaction} 
                      account={accountMap[transaction.account_id]}
                    />;
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan="6">
                      <Flex direction="column" alignItems="center" padding="2rem" gap="0.5rem">
                        <Heading level={5}>No Transactions Found</Heading>
                        <Text>There are no transactions for this account yet.</Text>
                      </Flex>
                    </TableCell>
                  </TableRow>
                )
              )}
            </TableBody>
          </Table>
          
          {transactions.length > 0 && !loading && (
            <Flex justifyContent="center" marginTop="1.5rem">
              <Button 
                isDisabled={!hasMorePages} 
                onClick={handleLoadMore} 
                size="small"
                variation="primary"
                isLoading={loading}
              >
                {hasMorePages ? 'Load More Transactions' : 'No More Transactions'}
              </Button>
            </Flex>
          )}
        </>
      )}
    </View>
  )
}
