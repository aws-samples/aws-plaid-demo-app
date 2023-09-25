import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');
const apiName = 'plaidapi';

export default function Plaid({ plaidUserToken, setPlaidUserToken, setPlaidToggle, plaidNumber, setPlaidNumber }) {
  const [showLink, setShowLink] = useState(false);

  // State to track Plaid variables.
  const [clientUserId, setClientUserId] = useState(null);
  const [linkToken, setLinkToken] = useState(null);

  // State to trigger Plaid requests.
  const [userRequest, setUserRequest] = useState(true);
  const [linkRequest, setLinkRequest] = useState(false);

  // Send Plaid requests depending on the values in state.
  useEffect(() => {
    if (userRequest) {
      sendUserRequest();
    }
  }, [userRequest]);

  useEffect(() => {
    if (linkRequest && plaidUserToken && clientUserId) sendLinkRequest();
  }, [linkRequest, plaidUserToken, clientUserId]);

  // Every time the # of requests left gets set, check to see if the process should be continued or ended.
  useEffect(() => {
    if (plaidNumber === 0) {
      setPlaidToggle(false);
    } else {
      setLinkRequest(true);
    }
  }, [plaidNumber]);

  // Starts the Plaid connection: gets the user token and triggers the opening of a Plaid Link.
  const sendUserRequest = async () => {
    // Create the user token.
    try {
      // Get the POST response and log it.
      const res = await API.get(apiName, '/v1/tokens/plaid-user');
      logger.debug('POST /v1/tokens/user response:', res);
      // Set user ID and token values asynchronously.
      setPlaidUserToken(res.user_token);
      setClientUserId(res.client_user_id);
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setLinkRequest(true);
    setUserRequest(false);
  };

  // Opens a Plaid link.
  const sendLinkRequest = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/plaid-link', {
        body: {
          user_token: plaidUserToken,
          client_user_id: clientUserId,
        },
      });
      logger.debug('POST /v1/tokens/link-payroll response:', res);
      setLinkToken(res.link_token);
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setShowLink(true);
    setLinkRequest(false);
  };

  // Determines whether a new plaid link should be created or the Plaid process is done.
  const handleLinkSuccess = async () => {
    setPlaidNumber(plaidNumber - 1);
  };

  console.log('PLAID')
  console.log(showLink)
  return showLink ? <PlaidLink token={linkToken} onSuccess={handleLinkSuccess} /> : null;
}