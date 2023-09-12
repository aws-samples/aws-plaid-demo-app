import { useEffect, useState } from 'react';
import { useAuthenticator } from '@aws-amplify/ui-react';
import { API, Logger } from 'aws-amplify';

const logger = new Logger('Covie');
const apiName = 'plaidapi';

export default function OnboardingForm() {
  // State to track Plaid variables.
  const [linkId, setLinkId] = useState(null);
  const [policies, setPolicies] = useState(null);
  const [policyRequest, setPolicyRequest] = useState(false);

  const setCovieState = (linkId, policies) => {
    setLinkId(linkId);
    setPolicies(policies);
    setPolicyRequest(true);
  };

  const sendPolicyRequest = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/auto-policy', {
        body: {
          policies: policies,
          email: userEmail,
        },
      });
      logger.debug('POST /v1/tokens/auto-policy response:', res);
    } catch (err) {
      logger.error('Unable to get policy info:', err);
    }
    setPolicyRequest(false);
  };

  // Send the policy request once the link is complete.
  useEffect(() => {
    if (policyRequest && policies) {
      sendPolicyRequest();
      setPolicyRequest(false);
    }
  }, [policyRequest, policies]);

  // Establish the link button. This code was provided by Covie.
  useEffect(() => {
    window.covieReady = () => {
      ' ';
    };
    {
      window.Covie.access.button({
        elementId: 'covie-root',
        buttonTheme: 'covie',
        buttonText: 'Link Insurance',
        embed: {
          integrationKey: 'ik_tgvz5zp57bq5jrij',
          linkId: '',
          metadata: {},
          hide: [],
          onSuccess: setCovieState,
        },
      });
    }
  }, []);

  return (
    <FormGroup>
      <FormControlLabel disabled control={<Switch />} label="Employment Verification" />
      <FormControlLabel control={<Switch defaultChecked />} label="Payroll Information" />
      <FormControlLabel control={<Switch defaultChecked />} label="Auto Insurance Policy" />
    </FormGroup>
  );
}
