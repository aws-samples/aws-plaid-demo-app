import { useState, useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader, View, Button } from '@aws-amplify/ui-react';
import Transaction from './Transaction';

const logger = new Logger("Transactions");

const apiName = "plaidapi";

export default function Transactions({ id, accounts = {} }) {

  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);

  const [nextToken, setNextToken] = useState(null);
  const [hasMorePages, setHasMorePages] = useState(false);

  const getTransactions = async () => {
    setLoading(true);
    try {
      const res = await API.get(apiName, `/v1/items/${id}/transactions`);
      logger.debug(`GET /v1/items/${id}/transactions response:`, res);
      setTransactions(res.transactions);
      if (res.cursor) {
        setHasMorePages(true);
        setNextToken(res.cursor);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get transactions', err);
    }
  }

  const handleLoadMore = async () => {
    const init = {
      queryStringParameters: {
        cursor: nextToken
      }
    }

    try {
      const res = await API.get(apiName, `/v1/items/${id}/transactions`, init);
      logger.debug(`GET /v1/items/${id}/transactions?cursor=${nextToken} response:`, res);
      if (res.cursor) {
        setNextToken(res.cursor);
        setHasMorePages(true);
      }
      else {
        setHasMorePages(false);
      }
      setTransactions([...transactions, ...res.transactions]);
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
                <TableCell colSpan="6">No transactions found</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
      <Button isDisabled={!hasMorePages} onClick={handleLoadMore} size="small" variable="primary">Load More</Button>
    </View>
  )
}
