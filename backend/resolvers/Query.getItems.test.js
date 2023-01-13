const { AppSyncClient, EvaluateCodeCommand } = require('@aws-sdk/client-appsync');
const fs = require('fs');

const client = new AppSyncClient({ region: 'us-east-1' });
const file = './Query.getItems.js';
const runtime = {
  name: 'APPSYNC_JS',
  runtimeVersion: '1.0.0',
};
const code = fs.readFileSync(file, { encoding: 'utf8' });

test('validate query items request', async () => {
  const context = JSON.stringify({
    arguments: {
      limit: 10,
      cursor: 'next-cursor',
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
  expect(result.query.expressionValues[':sk'].S).toEqual('USER#test-user#ITEM#');
});

test('validate query items response', async () => {
  const context = JSON.stringify({
    result: {
      items: [
        {
          sk: 'USER#test-user#ITEM#1234',
          institution_id: 1,
          institution_name: 'test-institution'
        }
      ],
      nextToken: 'next-cursor'
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
    function: 'response',
  };

  const command = new EvaluateCodeCommand(params);

  const response = await client.send(command);
  expect(response.error).toBeUndefined();
  expect(response.evaluationResult).toBeDefined();

  const result = JSON.parse(response.evaluationResult);

  const expected = {
    institution_id: 1,
    institution_name: 'test-institution',
    item_id: '1234'
  };

  expect(result).toHaveProperty('items');
  expect(result).toHaveProperty('cursor');
  expect(result.items[0]).toEqual(expected);
  expect(result.cursor).toEqual('next-cursor');
});
