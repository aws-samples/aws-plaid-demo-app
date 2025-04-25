import { useState } from 'react';
import { get, post } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new ConsoleLogger("Plaid");

const apiName = "plaidapi";

export default function Plaid({ getItems }) {
  const [connecting, setConnecting] = useState(false);
  const [token, setToken] = useState(null);

  const handleGetToken = async () => {
    setConnecting(true);
    try {
      const { body } = await get({
        apiName,
        path: '/v1/tokens'
      }).response;
      const data = await body.json();
      logger.debug('GET /v1/tokens response:', data);
      setToken(data.link_token);
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  const handleSuccess = async (public_token, metadata) => {
    try {
      const { body } = await post({
        apiName,
        path: '/v1/tokens',
        options: {
          body: {
            public_token,
            metadata
          },
        },
      }).response;
      const data = await body.text(); // returns an 202 response code with an empty body
      logger.debug('POST /v1/tokens response:', data);
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
