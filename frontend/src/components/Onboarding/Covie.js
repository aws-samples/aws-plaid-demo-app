import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';

const logger = new Logger('Covie');
const apiName = 'plaidapi';

export default function Covie({ setCovieToggle, setCoviePolicies }) {

  // State to track Covie variables.
  const [linkId, setLinkId] = useState(null);
  const [policyRequest, setPolicyRequest] = useState(false);

  const handleLinkSuccess = (linkId, policies) => {
    setLinkId(linkId);
    setCoviePolicies(policies);
    setCovieToggle(false);
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
    window.Covie.access.init({
      integrationKey: 'ik_tgvz5zp57bq5jrij',
      metadata: {},
      onSuccess: handleLinkSuccess,
    });
  }, []);

  return null;
}
