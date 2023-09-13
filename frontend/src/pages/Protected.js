import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import PlaidPayroll from '../components/PlaidPayroll';
import PlaidEmployment from '../components/PlaidEmployment';
import Covie from '../components/Covie';
import OnboardingForm from '../components/OnboardingForm';

export default function Protected() {

  const [plaidEmployment, setPlaidEmployment] = useState(true);
  const [plaidPayroll, setPlaidPayroll] = useState(true);
  const [covieInsurance, setCovieInsurance] = useState(true);

  return (
    <Flex direction="column">
      {plaidVisible ? <PlaidPayroll/> : null}
      {plaidVisible ? <PlaidEmployment/> : null}
      {covieVisible ? <Covie/> : null}
      <OnboardingForm
        plaidEmployment={plaidEmployment}
        setPlaidEmployment={setPlaidEmployment}
        plaidPayroll={plaidPayroll}
        setPlaidPayroll={setPlaidPayroll}
        covieInsurance={covieInsurance}
        setCovieInsurance={setCovieInsurance}
      />
    </Flex>
  );
}
