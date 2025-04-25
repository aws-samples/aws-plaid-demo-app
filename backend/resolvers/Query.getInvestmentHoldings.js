const AWS = require('aws-sdk');
const documentClient = new AWS.DynamoDB.DocumentClient();

/**
 * Retrieves investment holdings for a specific account
 */
exports.handler = async (event) => {
  const accountId = event.arguments.accountId;
  const userId = event.identity.sub;

  if (!accountId) {
    throw new Error('Account ID is required');
  }

  try {
    // First, find the item that this account belongs to
    const accountParams = {
      TableName: process.env.DYNAMODB_TABLE,
      IndexName: process.env.ACCOUNT_ID_INDEX,
      KeyConditionExpression: 'account_id = :accountId',
      ExpressionAttributeValues: {
        ':accountId': accountId
      }
    };

    const accountResult = await documentClient.query(accountParams).promise();
    
    if (!accountResult.Items || accountResult.Items.length === 0) {
      return [];
    }

    const account = accountResult.Items[0];
    // Extract item_id from the account's pk (format: USER#userId#ITEM#itemId)
    const pkParts = account.pk.split('#');
    const itemId = pkParts[3];
    
    // Query holdings for this account
    const holdingsParams = {
      TableName: process.env.DYNAMODB_TABLE,
      KeyConditionExpression: 'pk = :pk AND begins_with(sk, :sk)',
      ExpressionAttributeValues: {
        ':pk': `USER#${userId}#ITEM#${itemId}`,
        ':sk': `SECURITY#`
      }
    };

    const holdingsResult = await documentClient.query(holdingsParams).promise();
    
    // Filter for holdings that match this account and have quantity data
    const accountHoldings = holdingsResult.Items.filter(item => 
      item.plaid_type === 'Holding' && 
      item.account_id === accountId
    );

    // For each holding, fetch its associated security information
    const holdingsWithSecurities = await Promise.all(accountHoldings.map(async (holding) => {
      // Extract security_id from the holding's sk (format depends on data structure)
      const securityId = holding.security_id;
      
      // Query for the security details
      const securityParams = {
        TableName: process.env.DYNAMODB_TABLE,
        KeyConditionExpression: 'pk = :pk AND sk = :sk',
        ExpressionAttributeValues: {
          ':pk': `USER#${userId}#ITEM#${itemId}`,
          ':sk': `SECURITY#${securityId}`
        }
      };
      
      const securityResult = await documentClient.query(securityParams).promise();
      
      if (securityResult.Items && securityResult.Items.length > 0) {
        return {
          ...holding,
          security: securityResult.Items[0]
        };
      }
      
      return holding;
    }));

    return holdingsWithSecurities;
  } catch (error) {
    console.error('Error fetching investment holdings:', error);
    throw new Error(`Error fetching holdings: ${error.message}`);
  }
};