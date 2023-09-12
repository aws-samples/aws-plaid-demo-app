import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import PlaidPayroll from '../components/PlaidPayroll';
import PlaidEmployment from '../components/PlaidEmployment';
import Covie from '../components/Covie';
import Button from '@mui/material/Button';

const logger = new Logger("Protected");

export default function Protected() {

  // Variables used to show various buttons in the UI.
  const [plaidVisible, setPlaidVisible] = useState(true);
  const [covieVisible, setCovieVisible] = useState(true);

  return (
    <Flex direction="column">
      {plaidVisible ? <PlaidPayroll/> : null}
      {plaidVisible ? <PlaidEmployment/> : null}
      {covieVisible ? <Covie/> : null}
      <Button>Material UI Installed</Button>
    </Flex>
  );
}
