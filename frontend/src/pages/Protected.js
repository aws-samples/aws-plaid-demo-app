import { useState, useEffect } from 'react';
import { API, graphqlOperation, Logger } from 'aws-amplify';
import { View, Heading, Flex } from '@aws-amplify/ui-react';
import Plaid from '../components/Plaid';
import Covie from '../components/Covie';

import Institutions from '../components/Institutions';

const logger = new Logger("Protected");

export default function Protected() {

  return (
    <Flex direction="column">
      <Plaid/>
      <Covie/>
    </Flex>
  );
}
