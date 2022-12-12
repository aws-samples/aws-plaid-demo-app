import { useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger("Plaid");

const apiName = "plaidapi";

export default function Plaid({ getItems }) {
  const [connecting, setConnecting] = useState(false);
  const [token, setToken] = useState(null);

  const handleGetToken = async () => {
    setConnecting(true);
    try {
      const res = await API.get(apiName, '/v1/tokens');
      logger.debug('GET /v1/tokens response:', res);
      setToken(res.link_token);
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  const handleSuccess = async (public_token, metadata) => {
    try {
      const res = await API.post(apiName, '/v1/tokens', {
        body: {
          public_token,
          metadata
        }
      });
      logger.debug('POST /v1/tokens response:', res);
      getItems();
      setConnecting(false);
    } catch (err) {
      logger.error('unable to exchange public token', err);
    }
  };

  return (
    <Flex>
      <Button
        variation="primary"
        isLoading={connecting}
        onClick={handleGetToken}
      >
        CONNECT WITH PLAID
      </Button>
      {token ? (
        <PlaidLink
          token={token}
          onSuccess={handleSuccess}
          onExit={() => setConnecting(false)}
        />
      ) : null}
    </Flex>
  );
}
