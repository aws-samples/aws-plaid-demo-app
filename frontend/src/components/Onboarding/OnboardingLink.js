import * as React from 'react';
import { useState } from 'react';

import Plaid from './Plaid';
import Covie from './Covie';

export default function OnboardingLink({
  setOpen,
  plaidToggle,
  setPlaidToggle,
  plaidNumber,
  setPlaidNumber,
  covieToggle,
  setCovieToggle,
}) {

  // State needed to generate the Plaid email.
  const [plaidUserToken, setPlaidUserToken] = useState(null);
  const [plaidFinished, setPlaidFinished] = useState(null);

  if (plaidToggle) {
    return (
      <Plaid
        userToken={plaidUserToken}
        setUserToken={setPlaidUserToken}
        setPlaidFinished={setPlaidFinished}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
      />
    );
  } else if (covieToggle) {
    return <Covie />;
  } else {
    return setOpen(false);
  }
}
