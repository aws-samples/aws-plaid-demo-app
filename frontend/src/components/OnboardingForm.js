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

export default function OnboardingForm() {
  const [open, setOpen] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
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
            <FormControlLabel disabled control={<Switch />} label="Employment Verification" />
            <FormControlLabel control={<Switch defaultChecked />} label="Payroll Information" />
            <FormControlLabel control={<Switch defaultChecked />} label="Auto Insurance Policy" />
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