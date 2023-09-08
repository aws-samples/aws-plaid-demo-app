import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import PlaidPayroll from '../components/PlaidPayroll';
import PlaidEmployment from '../components/PlaidEmployment';
import Covie from '../components/Covie';

const logger = new Logger("Protected");

export default function Protected() {

  // Variables used to show various buttons in the UI.
  const [plaidVisible, setPlaidVisible] = useState(true);
  const [covieVisible, setCovieVisible] = useState(true);

  // Plaid tokens necessary for email generation.

  // Covie tokens necessaary for email generation.

  return (
    <Flex direction="column">
      {plaidVisible ? <PlaidPayroll/> : null}
      {plaidVisible ? <PlaidEmployment/> : null}
      {covieVisible ? <Covie/> : null}
    </Flex>
  );
}
