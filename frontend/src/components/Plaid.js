import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');

const apiName = 'plaidapi';

export default function Plaid({ getItems }) {
  const [connecting, setConnecting] = useState(false);
  const [public_token, setPublicToken] = useState(null);
  const [access_token, setAccessToken] = useState(null);

  const handleGetToken = async () => {
    setConnecting(true);
    try {
      const res = await API.get(apiName, '/v1/tokens');
      logger.debug('GET /v1/tokens response:', res);
      setPublicToken(res.link_token);
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
      setAccessToken(res.access_token);
    } catch (err) {
      logger.error('unable to exchange public token', err);
    }

    setConnecting(false);
  };

  useEffect(() => {
    if (access_token) {
      const getPayrollData = async() => {
        try {
          const res = await API.post(apiName, '/v1/tokens/payroll', {
            body: {
              user_token: access_token,
            },
          });
          logger.debug('POST /v1/payroll response:', res);
        } catch (err) {
          logger.error('unable to get payroll information', err);
        }
      }
      getPayrollData()
    }
  }, [access_token]);

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
