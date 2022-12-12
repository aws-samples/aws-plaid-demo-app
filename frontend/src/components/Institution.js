import { Link, TableRow, TableCell } from '@aws-amplify/ui-react';

export default function Institution({ institution }) {
  const link = `/institution/${institution.item_id}`;

  return (
    <TableRow>
      <TableCell>
        <Link href={link}>{ institution.institution_name }</Link>
      </TableCell>
    </TableRow>
  )
}
