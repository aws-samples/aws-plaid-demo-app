import { useEffect } from 'react';
import { API, Logger } from 'aws-amplify';

const apiName = 'plaidapi';
const logger = new Logger('PlaidInit');

export default function PlaidInit({ setUserRequest, setClientUserId, setUserToken }) {

  // Send Plaid requests depending on the values in state.
  useEffect(() => {
      sendUserRequest();
  }, []);

  // Starts the Plaid connection by getting a user token.
  const sendUserRequest = async () => {
    // Create the user token.
    try {
      // Get the POST response and log it.
      const res = await API.get(apiName, '/v1/tokens/user');
      logger.debug('POST /v1/tokens/user response:', res);
      // Set user ID and token values asynchronously.
      setUserToken(res.user_token);
      setClientUserId(res.client_user_id);
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setUserRequest(false);
  };

  return null;
}
