import { util } from '@aws-appsync/utils';

/**
 * Query DynamoDB for all transactions for a given user
 *
 * @param ctx the request context
 */
export function request(ctx) {
  const { username } = ctx.identity;
  const { id, limit = 20, cursor: nextToken } = ctx.arguments;

  return {
    operation: 'Query',
    query: {
      expression: '#pk = :pk AND BEGINS_WITH(#sk, :sk)',
      expressionNames: {
        '#pk': 'gsi1pk',
        '#sk': 'gsi1sk',
      },
      expressionValues: util.dynamodb.toMapValues({
        ':pk': `USER#${username}#ITEM#${id}#TRANSACTIONS`,
        ':sk': 'TRANSACTION#',
      }),
    },
    index: 'GSI1',
    scanIndexForward: false,
    limit,
    nextToken,
  };
}

/**
 * Returns the DynamoDB result
 *
 * @param ctx the request context
 */
export function response(ctx) {
  const { items: transactions = [], nextToken: cursor } = ctx.result;

  return {
    transactions,
    cursor,
  };
}
