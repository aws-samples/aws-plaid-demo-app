import { util } from '@aws-appsync/utils';

/**
 * Delete an item from DynamoDB
 *
 * @param ctx the request context
 */
export function request(ctx) {
  const { id } = ctx.arguments;
  const { username } = ctx.identity;

  // We'll use a batch operation to delete the item and all related records
  return {
    operation: 'TransactWriteItems',
    transactItems: [
      {
        table: 'InvestmentTable',
        operation: 'DeleteItem',
        key: util.dynamodb.toMapValues({
          pk: 'ITEMS',
          sk: `USER#${username}#ITEM#${id}`
        })
      }
      // Note: In a production environment, you would also delete all related
      // accounts, transactions, holdings, etc. for this item
      // This would require additional DeleteItem operations
    ]
  };
}

/**
 * Returns success or error based on DynamoDB result
 *
 * @param ctx the request context
 */
export function response(ctx) {
  const { error } = ctx;
  if (error) {
    return util.appendError(error.message, error.type, false);
  }
  return true;
}