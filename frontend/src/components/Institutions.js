import { Table, TableHead, TableRow, TableCell, TableBody } from '@aws-amplify/ui-react';
import Institution from './Institution';

export default function Institutions({ institutions = []}) {
  return (
    <Table highlightOnHover={true} variation="striped">
      <TableHead>
        <TableRow>
          <TableCell as="th">Name</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {institutions.length ? (
          institutions.map((institution) => {
            return <Institution key={institution.institution_id} institution={institution}/>;
          })
        ) : (
          <TableRow>
            <TableCell>No institutions found</TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
}
