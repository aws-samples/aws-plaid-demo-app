import { Link, TableRow, TableCell, Flex, Button } from '@aws-amplify/ui-react';

export default function Institution({ institution }) {
  const bankingLink = `/institution/${institution.item_id}`;
  const investmentLink = `/investment/${institution.item_id}`;

  return (
    <TableRow>
      <TableCell>
        <Flex direction="column" gap="0.5rem">
          <Link href={bankingLink}>{ institution.institution_name }</Link>
          <Flex direction="row" gap="0.5rem">
            <Button size="small" onClick={() => window.location.href = bankingLink}>
              Banking Dashboard
            </Button>
            <Button size="small" variation="primary" onClick={() => window.location.href = investmentLink}>
              Investment Dashboard
            </Button>
          </Flex>
        </Flex>
      </TableCell>
    </TableRow>
  )
}
