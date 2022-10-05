import { TableRow, TableCell } from '@aws-amplify/ui-react';
import Currency from './Currency';

export default function Transaction({ transaction, account }) {
  return (
    <TableRow>
      <TableCell>{ transaction.name }</TableCell>
      <TableCell>
        <Currency amount={ transaction.amount } currency={ transaction.iso_currency_code }/>
      </TableCell>
      <TableCell>{ transaction.date }</TableCell>
      <TableCell>{ account ? account.name : transaction.account_id }</TableCell>
      <TableCell>{ transaction.payment_channel }</TableCell>
      <TableCell>{ transaction.transaction_type }</TableCell>
    </TableRow>
  )
}
