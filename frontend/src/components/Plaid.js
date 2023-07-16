import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { useAuthenticator, Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');
const apiName = 'plaidapi';

export default function Plaid() {
  // Get lawyer's email to send data to.
  const { userEmail } = useAuthenticator((context) => context.user.signInUserSession.idToken.payload.email);
  
  // State to manipulate UI look.
  const [connecting, setConnecting] = useState(false);
  const [showLink, setShowLink] = useState(false);
  const [connectedAccount, setConnectedAccount] = useState(false);

  // State to track Plaid variables.
  const [clientUserId, setClientUserId] = useState(null);
  const [userToken, setUserToken] = useState(null);
  const [linkToken, setLinkToken] = useState(null);

  // State to trigge Plaid requests.
  const [userRequest, setUserRequest] = useState(false);
  const [linkRequest, setLinkRequest] = useState(false);
  const [payrollRequest, setPayrollRequest] = useState(false);

  // Send Plaid requests depending on the values in state.
  useEffect(() => {
    if (userRequest) {
      sendUserRequest();
    }
  }, [userRequest]);

  useEffect(() => {
    if (linkRequest && userToken && clientUserId) sendLinkRequest();
  }, [linkRequest, userToken, clientUserId]);

  useEffect(() => {
    if (payrollRequest && userToken) sendPayrollRequest();
  }, [payrollRequest, userToken]);

  // Starts the Plaid connection.
  // Gets the user token and then opens a Plaid Link.
  const sendUserRequest = async () => {
    // Disable the button.
    setConnecting(true);
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
    setConnecting(false);
  };

  // Opens a new Plaid link.
  const sendLinkRequest = async () => {
    setConnecting(true);
    try {
      const res = await API.post(apiName, '/v1/tokens/link-payroll', {
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
    setConnecting(false);
  };

  // Fetches plaid data on the remote server and sends it via email.
  const sendPayrollRequest = async () => {
    setConnecting(true);
    try {
      console.log('test')
      console.log(userEmail);
      const res = await API.post(apiName, '/v1/tokens/payroll', {
        body: {
          user_token: userToken,
          email: userEmail,
        },
      });
      console.log(userEmail);
      logger.debug('POST /v1/payroll response:', res);
    } catch (err) {
      logger.error('Unable to get payroll information', err);
    }
    setPayrollRequest(false);
    setConnecting(false);
  };

  const initialButtonClick = async () => {
    setUserRequest(true);
    setLinkRequest(true);
  };

  const subsequentButtonClick = async () => {
    setLinkRequest(true);
  };

  const getInitialButton = () => {
    return (
      <Button variation="primary" isLoading={connecting} onClick={initialButtonClick}>
        CONNECT WITH PLAID
      </Button>
    );
  };

  // Gets buttons
  const getSubsequentButtons = () => {
    return (
      <div>
        <Button variation="primary" isLoading={connecting} onClick={() => setLinkRequest(true)}>
          CONNECT ANOTHER ACCOUNT WITH PLAID
        </Button>
        <Button variation="primary" isLoading={connecting} onClick={() => setPayrollRequest(true)}>
          SEND EMAIL
        </Button>
      </div>
    );
  };

  return (
    <Flex>
      {connectedAccount ? getSubsequentButtons() : getInitialButton()}
      {showLink ? <PlaidLink token={linkToken} onSuccess={() => setConnectedAccount(true)} /> : null}
    </Flex>
  );
}
