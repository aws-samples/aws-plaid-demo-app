import * as React from 'react';
import { useState } from 'react';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import Plaid from './PlaidInit';
import Covie from './Covie';
import PlaidLinkController from './PlaidLinkController';

export default function OnboardingLink({
  // TODO: INSTALL REDUX!
  setOpen,
  plaidToggle,
  setPlaidToggle,
  plaidNumber,
  setPlaidNumber,
  covieToggle,
  setCovieToggle,
}) {

  const [createdPlaidUser, setCreatedPlaidUser] = useState(false);
  const [plaidUserToken, setPlaidUserToken] = useState(null);

  // Logic to close out a single Plaid link.
  const finishPlaidLink = () => {
    setPlaidNumber(plaidNumber - 1);
    if (plaidNumber === 0) {
      setPlaidToggle(0);
    }
  };

  // Logic to close out a single Covie Link.
  const finishCovieLink = () => {
    setCovieToggle(false);
  };

  if (plaidToggle) {
    return <PlaidLinkController createdUser={createdPlaidUser} setCreatedUser={setCreatedPlaidUser} setUserToken={setPlaidUserToken} finishLink={finishPlaidLink}/>;
  } else if (covieToggle) {
    return <Covie finishLink={finishCovieLink} />;
  } else {
    return setOpen(false);
  }
}
