import { util } from '@aws-appsync/utils';

/**
 * Query DynamoDB for all items for a given user
 *
 * @param ctx the request context
 */
export function request(ctx) {
  const { limit = 20, cursor: nextToken } = ctx.arguments;
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
        ':pk': 'ITEMS',
        ':sk': `USER#${username}#ITEM#`,
      }),
    },
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
  const { error, result } = ctx;
  if (error) {
    return util.appendError(error.message, error.type, result);
  }

  const { items = [], nextToken } = result;
  const { username } = ctx.identity;

  if (items.length === 0) {
    return {
      items: [],
    };
  }

  const institutions = [];

  // eslint-disable-next-line no-restricted-syntax
  for (const item of items) {
    const institution = {
      institution_id: item.institution_id,
      institution_name: item.institution_name,
      item_id: item.sk.replace(`USER#${username}#ITEM#`, ''),
    };
    institutions.push(institution);
  }

  return {
    items: institutions,
    cursor: nextToken,
  };
}
