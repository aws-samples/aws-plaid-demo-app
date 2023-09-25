import * as React from 'react';
import { useState } from 'react';

import Plaid from './Plaid';
import Covie from './Covie';

export default function OnboardingLink({
  open,
  setOpen,
  plaidToggle,
  setPlaidToggle,
  plaidNumber,
  setPlaidNumber,
  plaidUserToken,
  setPlaidUserToken,
  covieToggle,
  setCovieToggle,
  setCoviePolicies,
}) {
  console.log('OPEN');
  console.log(open);
  console.log('PLAID TOGGLE');
  console.log(plaidToggle);

  if (!open) {
    return null;
  } else if (plaidToggle) {
    return (
      <Plaid
        plaidUserToken={plaidUserToken}
        setPlaidUserToken={setPlaidUserToken}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
      />
    );
  } else if (covieToggle) {
    return <Covie setCovieToggle={setCovieToggle} setCoviePolicies={setCoviePolicies} />;
  } else {
    return setOpen(false);
  }
}
