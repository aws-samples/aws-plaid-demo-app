import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';
import Plaid from '../components/Plaid';
import Covie from '../components/Covie';

const logger = new Logger("Protected");

export default function Protected() {

  // Variables used to show various buttons in the UI.
  const [plaidVisible, setPlaidVisible] = useState(true);
  const [covieVisible, setCovieVisible] = useState(false);

  // Plaid tokens necessary for email generation.

  // Covie tokens necessaary for email generation.

  return (
    <Flex direction="column">
      <div id="covie-root"></div>
      <Button onClick={() => setCovieVisible(!covieVisible)}>Toggle Covie</Button>
      {plaidVisible ? <Plaid/> : null}
      {covieVisible ? <Covie/> : null}
    </Flex>
  );
}
