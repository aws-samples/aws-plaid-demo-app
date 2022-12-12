import { useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button } from '@aws-amplify/ui-react';

const logger = new Logger("Refresh");

const apiName = "plaidapi";

export default function Refresh({ item_id }) {
  const [loading, setLoading] = useState(false);

  const refresh = async() => {
    setLoading(true);
    try {
      const res = await API.post(apiName, `/v1/items/${item_id}/refresh`);
      logger.debug(`POST /v1/items/${item_id}/refresh response:`, res);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      logger.error('unable to refresh item', err);
    }
  }

  return (
    <Button isLoading={loading} onClick={refresh} size="small">Refresh Balances</Button>
  )
}
