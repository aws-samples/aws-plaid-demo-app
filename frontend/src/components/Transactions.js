import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader, View, Button } from '@aws-amplify/ui-react';
import Transaction from './Transaction';
import { getTransactions as GetTransactions } from '../graphql/queries';

const logger = new ConsoleLogger("Transactions");

export default function Transactions({ institutionId, accountMap = {} }) {

  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);

  const [nextToken, setNextToken] = useState(null);
  const [hasMorePages, setHasMorePages] = useState(false);

  const client = generateClient();

  const getTransactions = async () => {
    setLoading(true);
    try {
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId }
      });
      setTransactions(res.data.getTransactions.transactions);
      if (res.data.getTransactions.cursor) {
        setHasMorePages(true);
        setNextToken(res.data.getTransactions.cursor);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get transactions', err);
    }
  }

  const handleLoadMore = async () => {
    try {
      const res = await client.graphql({
        query: GetTransactions,
        variables: { id: institutionId, cursor: nextToken }
      });
      if (res.data.getTransactions.cursor) {
        setNextToken(res.data.getTransactions.cursor);
        setHasMorePages(true);
      }
      else {
        setHasMorePages(false);
      }
      setTransactions([...transactions, ...res.data.getTransactions.transactions]);
    } catch (err) {
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
              <Loader/>
            </TableCell>
          </TableRow>
          ) : (
            transactions.length ? (
              transactions.map((transaction) => {
                return <Transaction key={transaction.transaction_id} transaction={transaction} account={accountMap[transaction.account_id]}/>;
              })
            ) : (
              <TableRow>
                <TableCell colSpan="6">Waiting for transaction data...</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
      {transactions.length ? (
        <Button isDisabled={!hasMorePages} onClick={handleLoadMore} size="small" variable="primary">Load More</Button>
        ) : (
        <div/>
      )}
    </View>
  )
}
