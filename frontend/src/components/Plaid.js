import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { useAuthenticator, Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');

const apiName = 'plaidapi';

export default function Plaid() {
  const { userEmail } = useAuthenticator((context) => [context.user.signInUserSession.idToken.payload.email]);

  // State to manipulate UI.
  const [connecting, setConnecting] = useState(false);
  const [showLink, setShowLink] = useState(false);
  const [showButtons, setShowButtons] = useState(false);

  // State to maintain Plaid variables.  
  const [clientUserId, setClientUserId] = useState(null);
  const [userToken, setUserToken] = useState(null);
  const [linkToken, setLinkToken] = useState(null);

  const handleExit = async () => {
    // Check if the user token has been created.
  }

  // Gets new instance of a Plaid link. 
  const getNewLink = () => {
    return <PlaidLink token={linkToken} onSuccess={() => setShowButtons(true)} onExit={onExit} />;
  };

  // Starts the Plaid connection.
  // Gets the user token and then opens a Plaid Link.
  const startLink = async () => {
    // Disable the button.
    setConnecting(true);

    // Create the user token.
    try {
      // Get the POST response and log it.
      const res = await API.get(apiName, '/v1/tokens/user');
      logger.debug('POST /v1/tokens/user response:', res);
      // Set user ID and token values asynchronously.
      setUserToken(res.user_token),
        () => {
          setClientUserId(res.client_user_id),
            () => {
              openLink();
            };
        };
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  // Opens a new Plaid link.
  const openLink = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/link-payroll', {
        body: {
          client_user_id: clientUserId,
          user_token: userToken,
        },
      });
      logger.debug('POST /v1/tokens/link-payroll response:', res);
      setLinkToken(res.link_token, () => {
        setShowLink(true);
      });
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  const sendPayrollData = async () => {
    try {
      const res = await API.post(apiName, '/v1/tokens/payroll', {
        body: {
          user_token: userToken,
          email: userEmail,
        },
      });
      logger.debug('POST /v1/payroll response:', res);
    } catch (err) {
      logger.error('unable to get payroll information', err);
    }
    setConnecting(false);
  };

  const getButtons = async () => {
    return (
      <div>
          <Button variation="primary" onClick={openLink}>
            CONNECT AGAIN WITH PLAID
          </Button>
          <Button variation="primary" onClick={sendPayrollData}>
            SEND EMAIL
          </Button>
      </div>
    )
  }
  return (
    <Flex>
      <Button variation="primary" isLoading={connecting} onClick={openLink}>
        CONNECT WITH PLAID
      </Button>

      {showLink ? getNewLink() : null}
      {showButtons ? getButtons() : null}

    </Flex>
  );
}
