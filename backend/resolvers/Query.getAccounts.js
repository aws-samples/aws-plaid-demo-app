import { util } from '@aws-appsync/utils';

/**
 * Query DynamoDB for all accounts for a given user
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
        ':sk': 'ACCOUNT#',
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

  const accounts = [];
  // eslint-disable-next-line no-restricted-syntax
  for (const item of items) {
    // eslint-disable-next-line no-param-reassign
    item.account_id = item.sk.replace('ACCOUNT#', '');
    accounts.push(item);
  }

  return accounts;
}
