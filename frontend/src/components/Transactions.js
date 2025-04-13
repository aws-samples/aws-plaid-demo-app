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
    
    console.log("Fetching transactions for institution:", institutionId);
    
    try {
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId }
      });
      
      console.log("Transactions response:", res);
      
      if (res.data && res.data.getTransactions) {
        const transactionsList = res.data.getTransactions.transactions || [];
        console.log(`Loaded ${transactionsList.length} transactions`);
        
        setTransactions(transactionsList);
        
        if (res.data.getTransactions.cursor) {
          console.log("Pagination cursor available:", res.data.getTransactions.cursor);
          setHasMorePages(true);
          setNextToken(res.data.getTransactions.cursor);
        } else {
          console.log("No pagination cursor");
          setHasMorePages(false);
        }
      } else {
        console.warn("Unexpected response format:", res);
        setTransactions([]);
        setHasMorePages(false);
      }
    } catch (err) {
      console.error('Error fetching transactions:', err);
      setError('Failed to load transactions. Please see console for details.');
      logger.error('unable to get transactions', err);
    } finally {
      setLoading(false);
    }
  }

  const handleLoadMore = async () => {
    let isLoading = true;
    
    try {
      setError(null);
      console.log("Loading more transactions with cursor:", nextToken);
      
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId, cursor: nextToken }
      });
      
      console.log("Load more response:", res);
      
      if (res.data && res.data.getTransactions) {
        if (res.data.getTransactions.cursor) {
          console.log("New pagination cursor:", res.data.getTransactions.cursor);
          setNextToken(res.data.getTransactions.cursor);
          setHasMorePages(true);
        }
        else {
          console.log("No more transactions available");
          setHasMorePages(false);
        }
        
        if (res.data.getTransactions.transactions && res.data.getTransactions.transactions.length > 0) {
          const newTransactions = res.data.getTransactions.transactions;
          console.log(`Loaded ${newTransactions.length} more transactions`);
          setTransactions(prevTransactions => [...prevTransactions, ...newTransactions]);
        } else {
          console.log("No new transactions in response");
        }
      } else {
        console.warn("Unexpected load more response format:", res);
      }
      
      isLoading = false;
    } catch (err) {
      console.error("Error loading more transactions:", err);
      setError('Failed to load more transactions. See console for details.');
      logger.error('unable to get transactions', err);
      isLoading = false;
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
