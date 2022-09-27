import { useState, useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader } from '@aws-amplify/ui-react';
import Account from './Account';

const logger = new Logger("Accounts");

const apiName = "plaidapi";

export default function Accounts({ id, updateAccounts }) {

  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);

  const getAccounts = async () => {
    setLoading(true);
    try {
      const res = await API.get(apiName, `/v1/items/${id}/accounts`);
      logger.debug(`GET /v1/items/${id}/accounts response:`, res);
      setAccounts(res.accounts);
      updateAccounts(res.accounts);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get accounts', err);
    }
  }

  useEffect(() => {
    getAccounts();
  }, []);

  return (
    <Table highlightOnHover={true} variation="striped">
      <TableHead>
        <TableRow>
          <TableCell as="th">Name</TableCell>
          <TableCell as="th">Balances</TableCell>
          <TableCell as="th">Type</TableCell>
          <TableCell as="th">Subtype</TableCell>
          <TableCell as="th">Mask</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {loading ? (
        <TableRow>
          <TableCell colSpan="5">
            <Loader/>
          </TableCell>
        </TableRow>
        ) : (
          accounts.length ? (
            accounts.map((account) => {
              return <Account key={account.account_id} account={account}/>;
            })
          ) : (
            <TableRow>
              <TableCell colSpan="5">No accounts found</TableCell>
            </TableRow>
          )
        )}
      </TableBody>
    </Table>
  )
}
