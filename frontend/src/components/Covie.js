import { Logger } from 'aws-amplify';
import { useEffect, useState } from 'react';
import { useAuthenticator } from '@aws-amplify/ui-react';
import { API, Logger } from 'aws-amplify';

const logger = new Logger('Covie');
const apiName = 'plaidapi';

export default function Covie() {
  // Get lawyer's email to send data to.
  const { user } = useAuthenticator((context) => [context.user]);
  const userEmail = user.signInUserSession.idToken.payload.email;

  // State to track Plaid variables.
  const [linkId, setLinkId] = useState(null);
  const [policyIds, setPolicyIds] = useState(null);
  const [policyRequest, setPolicyRequest] = useState(false);

  const setCovieState = (linkId, policies) => {
    setLinkId(linkId);
    setPolicyIds(policies);
    setPolicyRequest(true);
  }

  const sendPolicyRequest = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/link-payroll', {
        body: {
          policy_ids: policyIds,
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
    if (policyRequest && policyIds) {
      sendPolicyRequest();
      setPolicyRequest(false);
    }
  }, [policyRequest, policyIds]);

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
          integrationKey: 'ik_emx55cdek5xtz2ro',
          linkId: '',
          metadata: {},
          hide: [],
          onSuccess: setCovieState,
        },
      });
    }
  }, []);

  return (
    <div>
      <div id="covie-root" />
    </div>
  );
}
