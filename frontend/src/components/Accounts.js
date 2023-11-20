import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader } from '@aws-amplify/ui-react';
import { getAccounts as GetAccounts } from '../graphql/queries';
import Account from './Account';

const logger = new ConsoleLogger("Accounts");

export default function Accounts({ id, updateAccounts }) {

  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);

  const client = generateClient();

  const getAccounts = async () => {
    setLoading(true);
    try {
      const res = await client.graphql({
        query: GetAccounts,
        variables: { id }
      });
      setAccounts(res.data.getAccounts);
      updateAccounts(res.data.getAccounts);
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
