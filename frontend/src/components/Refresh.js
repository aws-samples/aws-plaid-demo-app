import { useState } from 'react';
import { post } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { Button } from '@aws-amplify/ui-react';

const logger = new ConsoleLogger("Refresh");

const apiName = "plaidapi";

export default function Refresh({ item_id }) {
  const [loading, setLoading] = useState(false);

  const refresh = async() => {
    setLoading(true);
    try {
      const { body } = await post({
        apiName,
        path: `/v1/items/${item_id}/refresh`
      }).response;
      const data = await body.json();
      logger.debug(`POST /v1/items/${item_id}/refresh response:`, data);
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
