import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import PlaidPayroll from '../components/PlaidPayroll';
import PlaidEmployment from '../components/PlaidEmployment';
import Covie from '../components/Covie';
import OnboardingForm from '../components/OnboardingForm';

export default function Protected() {

  const [plaidToggle, setPlaidToggle] = useState(true);
  const [plaidNumber, setPlaidNumber] = useState(true);
  const [covieToggle, setCovieToggle] = useState(true);

  return (
    <Flex direction="column">
      <PlaidPayroll/>
      <PlaidEmployment/>
      <Covie/>
      <OnboardingForm
        plaidToggle={plaidToggle}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
        covieToggle={covieToggle}
        setCovieToggle={covieToggle}
      />
    </Flex>
  );
}
