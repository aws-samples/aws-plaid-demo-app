import { TableRow, TableCell } from '@aws-amplify/ui-react';
import Currency from './Currency';

export default function Account({ account }) {
  return (
    <TableRow>
      <TableCell>{ account.name }</TableCell>
      <TableCell>
        <Currency amount={ account.balances?.current} currency={ account.balances?.iso_currency_code }/>
      </TableCell>
      <TableCell>{ account.type }</TableCell>
      <TableCell>{ account.subtype }</TableCell>
      <TableCell>****{ account.mask }</TableCell>
    </TableRow>
  )
}
