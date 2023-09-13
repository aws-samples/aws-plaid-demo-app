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

export default function OnboardingForm({
  plaidEmployment,
  setPlaidEmployment,
  plaidPayroll,
  setPlaidPayroll,
  covieInsurance,
  setCovieInsurance,
}) {
  const [open, setOpen] = useState(false);

  const handleClose = () => {
    setOpen(false);
  };

  const handleFormGeneration = () => {
    setOpen(false);
  };

  const getPlaidEmploymentSwitch = () => {
    return (
      <Switch
        checked={plaidEmployment}
        onChange={(event) => setPlaidEmployment(event.target.checked)}
      />
    );
  };

  const getPlaidPayrollSwitch = () => {
    return (
      <Switch
        checked={plaidPayroll}
        onChange={(event) => setPlaidPayroll(event.target.checked)}
      />
    );
  };

  const getCovieInsuranceSwitch = () => {
    return (
      <Switch
        checked={covieInsurance}
        onChange={(event) => setCovieInsurance(event.target.checked)}
      />
    );
  };

  return (
    <div>
      <Button variant="outlined" onClick={handleClickOpen}>
        Generate Onboarding Form
      </Button>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Generate Claimant Form</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Please check the infomtaion that you would like to pull for the claimant.
          </DialogContentText>
          <FormGroup>
            <FormControlLabel control={getPlaidEmploymentSwitch()} label="Employment Verification" />
            <FormControlLabel control={getPlaidPayrollSwitch()} label="Payroll Information" />
            <FormControlLabel control={getCovieInsuranceSwitch()} label="Auto Insurance Policy" />
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleClose}>Generate</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
