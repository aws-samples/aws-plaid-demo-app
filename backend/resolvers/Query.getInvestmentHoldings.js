import { util } from '@aws-appsync/utils';

/**
 * Query DynamoDB for all investment holdings for a given user's item
 *
 * @param ctx the request context
 */
export function request(ctx) {
  const { id } = ctx.arguments;
  const { username } = ctx.identity;

  return {
    operation: 'Query',
    query: {
      expression: '#pk = :pk AND begins_with(#sk, :sk)',
      expressionNames: {
        '#pk': 'pk',
        '#sk': 'sk',
      },
      expressionValues: util.dynamodb.toMapValues({
        ':pk': `USER#${username}#ITEM#${id}`,
        ':sk': 'HOLDING#',
      }),
    },
    limit: 100,
  };
}

/**
 * Returns the DynamoDB result
 *
 * @param ctx the request context
 */
export function response(ctx) {
  const { error, result } = ctx;
  if (error) {
    return util.appendError(error.message, error.type, result);
  }

  const { items = [] } = result;

  if (items.length === 0) {
    return [];
  }

  const holdings = [];
  // eslint-disable-next-line no-restricted-syntax
  for (const item of items) {
    // Parse the SK to extract the security_id
    const parts = item.sk.split('#');
    if (parts.length >= 3) {
      item.security_id = parts[2];
      item.account_id = parts[1].replace('ACCOUNT', '');
    }
    
    // Ensure quantity is a number
    if (item.quantity && typeof item.quantity === 'string') {
      item.quantity = parseFloat(item.quantity);
    }
    
    // Ensure prices are numbers
    if (item.institution_price && typeof item.institution_price === 'string') {
      item.institution_price = parseFloat(item.institution_price);
    }
    
    if (item.cost_basis && typeof item.cost_basis === 'string') {
      item.cost_basis = parseFloat(item.cost_basis);
    }
    
    holdings.push(item);
  }

  return holdings;
}