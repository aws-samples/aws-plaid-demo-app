import { useState, useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Loader, View, Heading, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';
import Institutions from './Institutions';

const logger = new Logger("Plaid");

const apiName = "plaidapi";

export default function Plaid() {
  const [connecting, setConnecting] = useState(false);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);

  const getItems = async () => {
    setLoading(true);
    try {
      const res = await API.get(apiName, '/v1/items');
      logger.debug('GET /v1/items response:', res);
      setItems(res.items);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to get items', err);
    }
  }

  useEffect(() => {
    getItems();
  }, []);

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
    } catch (err) {
      logger.error('unable to exchange public token', err);
    }
  };

  if (loading) {
    return (
      <View>
        <Loader />
      </View>
    );
  }

  if (items && items.length) {
    return (
      <View>
        <Heading>Institutions</Heading>
        <Institutions institutions={items}/>
      </View>
    );
  }

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
