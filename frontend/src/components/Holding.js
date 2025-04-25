import { TableRow, TableCell } from '@aws-amplify/ui-react';
import Currency from './Currency';

export default function Holding({ holding, account }) {
  const marketValue = holding.institution_price * holding.quantity;
  const costBasis = holding.cost_basis ? holding.cost_basis * holding.quantity : null;
  
  // Calculate return if both values are available
  let returnValue = null;
  let returnPercent = null;
  if (costBasis && marketValue) {
    returnValue = marketValue - costBasis;
    returnPercent = (returnValue / costBasis) * 100;
  }
  
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <TableRow>
      <TableCell>{ holding.security?.ticker_symbol || 'Unknown' }</TableCell>
      <TableCell>{ holding.security?.name || 'Unknown' }</TableCell>
      <TableCell>
        <Currency amount={ holding.institution_price } currency={ holding.currency } />
      </TableCell>
      <TableCell>{ formatDate(holding.institution_price_as_of) }</TableCell>
      <TableCell>{ holding.quantity.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 8 }) }</TableCell>
      <TableCell>
        <Currency amount={ marketValue } currency={ holding.currency } />
      </TableCell>
      {costBasis && (
        <>
          <TableCell>
            <Currency amount={ costBasis } currency={ holding.currency } />
          </TableCell>
          <TableCell style={{ color: returnValue >= 0 ? 'green' : 'red' }}>
            <Currency amount={ returnValue } currency={ holding.currency } />
            {returnPercent !== null && ` (${returnPercent.toFixed(2)}%)`}
          </TableCell>
        </>
      )}
      <TableCell>{ account?.name || 'Unknown' }</TableCell>
    </TableRow>
  )
}