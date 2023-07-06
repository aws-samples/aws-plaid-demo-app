import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');

const apiName = 'plaidapi';
const TEST_CLIENT_USER_ID = 'test1';

export default function Plaid({ getItems }) {
  const [connecting, setConnecting] = useState(false);
  const [user_id, setUserId] = useState(null);
  const [user_token, setUserToken] = useState(null);
  const [public_token, setPublicToken] = useState(null);

  const handleGetToken = async () => {
    setConnecting(true);
    // TODO: Make the async chained.
    var userId;
    var userToken;

    // Create the user token.
    try {
      const res = await API.post(apiName, '/v1/tokens/user', {
        body: {
          client_user_id: TEST_CLIENT_USER_ID,
        },
      });
      logger.debug('POST /v1/tokens/user response:', res);
      setUserId(res.user_id);
      userId = res.user_id;
      setUserToken(res.user_token);
      userToken = res.userToken;
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
    // Create the link.
    try {
      const res = await API.get(apiName, '/v1/tokens/link', {
        body: {
          client_user_id: TEST_CLIENT_USER_ID,
          user_token: user_token
        },
      });
      logger.debug('POST /v1/tokens/user response:', res);
      setUserId(res.user_id);
      userId = res.user_id;
      setUserToken(res.user_token);
      userToken = res.userToken;
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  const handleSuccess = async (public_token, metadata) => {
    try {
      const res = await API.post(apiName, '/v1/tokens', {
        body: {
          public_token,
          metadata,
        },
      });
      logger.debug('POST /v1/tokens response:', res);
      setUserToken(res.access_token);
    } catch (err) {
      logger.error('unable to exchange public token', err);
    }

    setConnecting(false);
  };

  useEffect(() => {
    if (user_token) {
      const getPayrollData = async () => {
        try {
          const res = await API.post(apiName, '/v1/tokens/payroll', {
            body: {
              user_token: user_token,
            },
          });
          logger.debug('POST /v1/payroll response:', res);
        } catch (err) {
          logger.error('unable to get payroll information', err);
        }
      };
      getPayrollData();
    }
  }, [user_token]);

  return (
    <Flex>
      <Button variation="primary" isLoading={connecting} onClick={handleGetToken}>
        CONNECT WITH PLAID
      </Button>
      {public_token ? (
        <PlaidLink token={public_token} onSuccess={handleSuccess} onExit={() => setConnecting(false)} />
      ) : null}
    </Flex>
  );
}
