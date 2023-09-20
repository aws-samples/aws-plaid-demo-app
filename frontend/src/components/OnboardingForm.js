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

export default function OnboardingForm({
  // TODO: INSTALL REDUX!
  plaidToggle,
  setPlaidToggle,
  plaidNumber,
  setPlaidNumber,
  covieToggle,
  setCovieToggle,
}) {
  // Displays whether the onboarding form is visible.
  const [open, setOpen] = useState(false);

  const handleFormGeneration = () => {
    setOpen(true);
  };

  const handleFormSubmission = () => {
    setOpen(false);
  };

  // For now, there is no health data.
  const getHealthDataSwitch = () => {
    return <Switch checked={false} disabled />;
  };

  // Returns switch to indicate if we want to use Plaid APIs.
  const getPlaidSwitch = () => {
    return <Switch checked={plaidToggle} onChange={(event) => setPlaidToggle(event.target.checked)} />;
  };

  // Returns the number of pay stubs to pull.
  const getPlaidNumberInput = () => {
    return (
      <TextField
        id="outlined-required"
        label="Number of Employments To Verify"
        value={plaidNumber}
        onChange={(event) => setPlaidNumber(event.target.value)}
        type="number"
      />
    );
  };

  const getCovieSwitch = () => {
    return <Switch checked={covieToggle} onChange={(event) => setCovieToggle(event.target.checked)} />;
  };

  return (
    <div>
      <Button variant="outlined" onClick={handleFormGeneration}>
        Generate Onboarding Form
      </Button>

      <Dialog open={open} onClose={handleFormSubmission}>
        <DialogTitle>Generate Claimant Form!</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Please note the information that you would like to pull for the claimant.
          </DialogContentText>
          <FormGroup>
            <FormControlLabel control={getHealthDataSwitch()} label="Health Data" />
            <FormControlLabel control={getPlaidSwitch()} label="Employment Data" />
            {/* Only render the # input if the toggle is checked for Plaid. */}
            {plaidToggle ? <FormControlLabel control={getPlaidNumberInput()} label="Payroll Information" /> : null}
            <FormControlLabel control={getCovieSwitch()} label="Auto Insurance Data" />
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
