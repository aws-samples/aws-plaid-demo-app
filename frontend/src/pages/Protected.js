import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/api';
import { ConsoleLogger } from 'aws-amplify/utils';
import { View, Heading, Flex } from '@aws-amplify/ui-react';
import { getItems as GetItems } from '../graphql/queries';
import Plaid from '../components/Plaid';
import Institutions from '../components/Institutions';

const logger = new ConsoleLogger("Protected");

export default function Protected() {
  const [items, setItems] = useState([]);
  const client = generateClient();

  const getItems = async () => {
    try {
      const res = await client.graphql({
        query: GetItems
      });
      logger.info(res);
      setItems(res.data.getItems.items);
    } catch (err) {
      logger.error('unable to get items', err);
    }
  }

  useEffect(() => {
    getItems();
  }, []);

  return (
    <Flex direction="column">
      <Plaid getItems={getItems}/>
      {(items && items.length) ? (
        <View>
          <Heading>Institutions</Heading>
          <Institutions institutions={items}/>
        </View>
      ) : (<div/>)
      }
    </Flex>
  );
}
