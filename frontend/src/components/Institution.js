import { Link, TableRow, TableCell, Button, Flex, Text } from '@aws-amplify/ui-react';

export default function Institution({ institution, isManagementView = false }) {
  const link = `/institution/${institution.item_id}`;
  
  // Function to format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Placeholder for disconnect functionality
  const handleDisconnect = () => {
    // This would need to be implemented to call the API to disconnect the institution
    console.log('Disconnect institution:', institution.item_id);
    alert('This feature is not yet implemented.');
  };

  return (
    <TableRow>
      <TableCell>
        <Link href={link}>{ institution.institution_name }</Link>
      </TableCell>
      
      {isManagementView && (
        <TableCell>
          <Text>{formatDate(institution.updated_at)}</Text>
        </TableCell>
      )}
      
      {isManagementView && (
        <TableCell>
          <Flex gap="0.5rem">
            <Button
              size="small"
              variation="link"
              onClick={() => window.location.href = link}
            >
              View Details
            </Button>
            <Button
              size="small"
              variation="destructive"
              onClick={handleDisconnect}
            >
              Disconnect
            </Button>
          </Flex>
        </TableCell>
      )}
    </TableRow>
  )
}
