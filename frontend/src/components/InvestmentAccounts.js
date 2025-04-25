import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader } from '@aws-amplify/ui-react';
import { getInvestmentAccounts as GetInvestmentAccounts } from '../graphql/queries';
import InvestmentAccount from './InvestmentAccount';

const logger = new ConsoleLogger("InvestmentAccounts");

export default function InvestmentAccounts({ id, updateAccounts }) {

  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);

  const client = generateClient();

  const getInvestmentAccounts = async () => {
    setLoading(true);
    try {
      const res = await client.graphql({
        query: GetInvestmentAccounts,
        variables: { id }
      });
      setAccounts(res.data.getInvestmentAccounts);
      updateAccounts(res.data.getInvestmentAccounts);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get investment accounts', err);
    }
  }

  useEffect(() => {
    getInvestmentAccounts();
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
              return <InvestmentAccount key={account.account_id} account={account}/>;
            })
          ) : (
            <TableRow>
              <TableCell colSpan="5">No investment accounts found</TableCell>
            </TableRow>
          )
        )}
      </TableBody>
    </Table>
  )
}