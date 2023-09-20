import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { useAuthenticator, Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';
import PlaidInit from './PlaidInit';

const logger = new Logger('Plaid');
const apiName = 'plaidapi';

export default function PlaidLinkController({ setUserToken, finishLink }) {
  // State to manipulate UI look.
  const [showLink, setShowLink] = useState(false);

  // State to track tokens and IDs.
  const [clientUserId, setClientUserId] = useState(null);
  const [linkToken, setLinkToken] = useState(null);

  // State to trigger Plaid requests.
  const [userRequest, setUserRequest] = useState(true);
  const [linkRequest, setLinkRequest] = useState(false);
  const [payrollRequest, setPayrollRequest] = useState(false);

  // Send Plaid requests depending on the values in state.
  useEffect(() => {
    if (userRequest) {
      return <PlaidInit setUserRequest={setUserRequest} setClientUserId={setClientUserId} setUserToken={setUserToken} />;
    }
  }, [userRequest]);

  // Left off here. In theory, when a plaid link controller gets rendered, it should send out the user request. Now, need to handle opening the correct # of links and moving the user token into its own logic.
  // PlaidLinkCreator should get the link token and then open the link. When done, it should call finishLink().
  useEffect(() => {
    if (linkRequest && clientUserId && userToken) sendLinkRequest();
  }, [linkRequest, clientUserId, userToken]);

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
      const res = await API.post(apiName, '/v1/tokens/payroll', {
        body: {
          user_token: userToken,
          email: userEmail,
        },
      });
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
