import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Table, TableHead, TableRow, TableCell, TableBody, Loader, Text } from '@aws-amplify/ui-react';
import { getInvestmentHoldings as GetInvestmentHoldings } from '../graphql/queries';
import Holding from './Holding';
import Currency from './Currency';

const logger = new ConsoleLogger("Holdings");

export default function Holdings({ id, accounts }) {
  const [loading, setLoading] = useState(true);
  const [holdings, setHoldings] = useState([]);
  const [totalValue, setTotalValue] = useState(0);
  const [currency, setCurrency] = useState('USD');

  const client = generateClient();

  const getHoldings = async () => {
    setLoading(true);
    try {
      const res = await client.graphql({
        query: GetInvestmentHoldings,
        variables: { id }
      });
      
      const fetchedHoldings = res.data.getInvestmentHoldings || [];
      setHoldings(fetchedHoldings);
      
      // Calculate total portfolio value
      let portfolioValue = 0;
      let mainCurrency = 'USD';
      
      if (fetchedHoldings.length > 0) {
        mainCurrency = fetchedHoldings[0].currency;
        portfolioValue = fetchedHoldings.reduce((sum, holding) => {
          // Only sum holdings with the same currency
          if (holding.currency === mainCurrency) {
            return sum + (holding.institution_price * holding.quantity);
          }
          return sum;
        }, 0);
      }
      
      setTotalValue(portfolioValue);
      setCurrency(mainCurrency);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get investment holdings', err);
    }
  }

  useEffect(() => {
    getHoldings();
  }, []);

  const hasCostBasis = holdings.some(holding => holding.cost_basis !== null && holding.cost_basis !== undefined);

  return (
    <>
      <div style={{ marginBottom: '1rem', textAlign: 'right' }}>
        <Text fontSize="large" fontWeight="bold">
          Total Portfolio Value: <Currency amount={totalValue} currency={currency} />
        </Text>
      </div>
      <Table highlightOnHover={true} variation="striped">
        <TableHead>
          <TableRow>
            <TableCell as="th">Symbol</TableCell>
            <TableCell as="th">Name</TableCell>
            <TableCell as="th">Price</TableCell>
            <TableCell as="th">As Of</TableCell>
            <TableCell as="th">Quantity</TableCell>
            <TableCell as="th">Market Value</TableCell>
            {hasCostBasis && (
              <>
                <TableCell as="th">Cost Basis</TableCell>
                <TableCell as="th">Return</TableCell>
              </>
            )}
            <TableCell as="th">Account</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
          <TableRow>
            <TableCell colSpan={hasCostBasis ? "9" : "7"}>
              <Loader/>
            </TableCell>
          </TableRow>
          ) : (
            holdings.length ? (
              holdings.map((holding) => {
                const account = accounts[holding.account_id];
                return <Holding key={`${holding.account_id}-${holding.security_id}`} holding={holding} account={account}/>;
              })
            ) : (
              <TableRow>
                <TableCell colSpan={hasCostBasis ? "9" : "7"}>No holdings found</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
    </>
  )
}