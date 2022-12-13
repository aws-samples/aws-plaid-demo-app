const { AppSyncClient, EvaluateCodeCommand } = require('@aws-sdk/client-appsync');
const fs = require('fs');

const client = new AppSyncClient({ region: 'us-east-1' });
const file = './Query.getTransactions.js';
const runtime = {
  name: 'APPSYNC_JS',
  runtimeVersion: '1.0.0',
};
const code = fs.readFileSync(file, { encoding: 'utf8' });

test('validate query transactions request', async () => {
  const context = JSON.stringify({
    arguments: {
      limit: 10,
      cursor: 'next-cursor',
      id: '1234'
    },
    identity: {
      sourceIp: ['127.0.0.1'],
      username: 'test-user',
      groups: null,
      sub: 'test-user',
      issuer: 'cognito',
      claims: {},
      defaultAuthStrategy: 'ALLOW'
    },
  });

  const params = {
    context,
    code,
    runtime,
    function: 'request',
  };

  const command = new EvaluateCodeCommand(params);

  const response = await client.send(command);
  expect(response.error).toBeUndefined();
  expect(response.evaluationResult).toBeDefined();

  const result = JSON.parse(response.evaluationResult);

  expect(result.query.expressionNames).toHaveProperty('#pk');
  expect(result.query.expressionNames).toHaveProperty('#sk');
  expect(result.query.expressionValues).toHaveProperty(':pk');
  expect(result.query.expressionValues).toHaveProperty(':sk');
  expect(result.query.expressionValues[':pk'].S).toEqual('USER#test-user#ITEM#1234#TRANSACTIONS');
  expect(result.query.expressionValues[':sk'].S).toEqual('TRANSACTION#');
  expect(result.limit).toEqual(10);
  expect(result.nextToken).toEqual('next-cursor');
});

test('validate query transactions response', async () => {
  const context = JSON.stringify({
    result: {
      items: [
        {
          'key': 1
        }
      ],
      nextToken: 'next-cursor'
    }
  });

  const params = {
    context,
    code,
    runtime,
    function: 'response',
  };

  const command = new EvaluateCodeCommand(params);

  const response = await client.send(command);
  expect(response.error).toBeUndefined();
  expect(response.evaluationResult).toBeDefined();

  const result = JSON.parse(response.evaluationResult);

  expect(result).toHaveProperty('transactions');
  expect(result).toHaveProperty('cursor');
  expect(result.transactions[0]).toEqual({'key': 1});
  expect(result.cursor).toEqual('next-cursor');
});
