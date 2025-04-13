import { Table, TableHead, TableRow, TableCell, TableBody, Text } from '@aws-amplify/ui-react';
import Institution from './Institution';

export default function Institutions({ institutions = [], loading = false, isManagementView = false }) {
  return (
    <Table highlightOnHover={true} variation="striped">
      <TableHead>
        <TableRow>
          <TableCell as="th">Name</TableCell>
          {isManagementView && <TableCell as="th">Last Updated</TableCell>}
          {isManagementView && <TableCell as="th">Actions</TableCell>}
        </TableRow>
      </TableHead>
      <TableBody>
        {loading ? (
          <TableRow>
            <TableCell colSpan={isManagementView ? 3 : 1}>
              <Text>Loading institutions...</Text>
            </TableCell>
          </TableRow>
        ) : institutions.length ? (
          institutions.map((institution) => {
            return <Institution 
              key={institution.institution_id} 
              institution={institution}
              isManagementView={isManagementView}
            />;
          })
        ) : (
          <TableRow>
            <TableCell colSpan={isManagementView ? 3 : 1}>No institutions found</TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  )
}
