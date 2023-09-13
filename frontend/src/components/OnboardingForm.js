import { useState } from 'react';
import { Logger } from 'aws-amplify';

import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';

const logger = new Logger('Covie');
const apiName = 'plaidapi';

export default function OnboardingForm() {

  // State to track Plaid variables.
  const [linkId, setLinkId] = useState(null);
  const [policies, setPolicies] = useState(null);
  const [policyRequest, setPolicyRequest] = useState(false);

  return (
    <FormGroup>
      <FormControlLabel disabled control={<Switch />} label="Employment Verification" />
      <FormControlLabel control={<Switch defaultChecked />} label="Payroll Information" />
      <FormControlLabel control={<Switch defaultChecked />} label="Auto Insurance Policy" />
    </FormGroup>
  );
}
