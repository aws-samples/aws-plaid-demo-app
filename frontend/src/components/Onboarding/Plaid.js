import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');
const apiName = 'plaidapi';

export default function Plaid({ userToken, setUserToken, setPlaidFinished, setPlaidToggle, plaidNumber, setPlaidNumber }) {
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
    if (linkRequest && userToken && clientUserId) sendLinkRequest();
  }, [linkRequest, userToken, clientUserId]);

  // Starts the Plaid connection: gets the user token and triggers the opening of a Plaid Link.
  const sendUserRequest = async () => {
    // Create the user token.
    try {
      // Get the POST response and log it.
      const res = await API.get(apiName, '/v1/tokens/plaid-user');
      logger.debug('POST /v1/tokens/user response:', res);
      // Set user ID and token values asynchronously.
      setUserToken(res.user_token);
      setClientUserId(res.client_user_id);
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setUserRequest(false);
  };

  // Opens a Plaid link.
  const sendLinkRequest = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/plaid-link', {
        body: {
          user_token: userToken,
          client_user_id: clientUserId,
        },
      });
      logger.debug('POST /v1/tokens/link-payroll response:', res);
      setLinkToken(res.link_token);
      setShowLink(true);
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setLinkRequest(false);
  };

  // Determines whether a new plaid link should be created or the Plaid process is done.
  const finishLink = async () => {
    setPlaidNumber(plaidNumber - 1);
    if (plaidNumber === 0) {
      setPlaidToggle(false);
    }
  };

  console.log('PLAID')
  console.log(showLink)
  return showLink ? <PlaidLink token={linkToken} onSuccess={finishLink} /> : null;
}
