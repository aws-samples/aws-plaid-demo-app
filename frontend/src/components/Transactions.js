import { useState, useEffect } from 'react';
import { API, graphqlOperation, Logger } from 'aws-amplify';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader, View, Button } from '@aws-amplify/ui-react';
import Transaction from './Transaction';
import { getTransactions as GetTransactions } from '../graphql/queries';

const logger = new Logger("Transactions");

export default function Transactions({ id, accounts = {} }) {

  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);

  const [nextToken, setNextToken] = useState(null);
  const [hasMorePages, setHasMorePages] = useState(false);

  const getTransactions = async () => {
    setLoading(true);
    try {
      const res = await API.graphql(graphqlOperation(GetTransactions, { id }));
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
      const res = await API.graphql(graphqlOperation(GetTransactions, { id, cursor: nextToken }));
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
    getTransactions();
  }, []);

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
                return <Transaction key={transaction.transaction_id} transaction={transaction} account={accounts[transaction.account_id]}/>;
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
