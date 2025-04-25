const AWS = require('aws-sdk');
const documentClient = new AWS.DynamoDB.DocumentClient();

/**
 * Retrieves investment accounts associated with a specific item
 * Filters accounts to only include those with type 'investment' or related subtypes
 */
exports.handler = async (event) => {
  const itemId = event.arguments.id;
  const userId = event.identity.sub;

  if (!itemId) {
    throw new Error('Item ID is required');
  }

  try {
    // Query all accounts for this item
    const params = {
      TableName: process.env.DYNAMODB_TABLE,
      KeyConditionExpression: 'pk = :pk AND begins_with(sk, :sk)',
      ExpressionAttributeValues: {
        ':pk': `USER#${userId}#ITEM#${itemId}`,
        ':sk': 'ACCOUNT#'
      }
    };

    const result = await documentClient.query(params).promise();
    
    // Filter for only investment accounts
    const investmentAccounts = result.Items.filter(account => {
      return (
        account.type === 'investment' || 
        account.subtype === 'investment' ||
        (account.subtype && account.subtype.includes('retirement')) ||
        (account.subtype && account.subtype.includes('brokerage'))
      );
    });

    return investmentAccounts;
  } catch (error) {
    console.error('Error fetching investment accounts:', error);
    throw new Error(`Error fetching accounts: ${error.message}`);
  }
};