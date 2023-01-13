const { AppSyncClient, EvaluateCodeCommand } = require('@aws-sdk/client-appsync');
const fs = require('fs');

const client = new AppSyncClient({ region: 'us-east-1' });
const file = './Query.getAccounts.js';
const runtime = {
  name: 'APPSYNC_JS',
  runtimeVersion: '1.0.0',
};
const code = fs.readFileSync(file, { encoding: 'utf8' });

test('validate query accounts request', async () => {
  const context = JSON.stringify({
    arguments: {
      id: 'item-id',
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
});

test('validate query accounts response', async () => {
  const context = JSON.stringify({
    result: {
      items: [
        {
          sk: 'ACCOUNT#1234'
        }
      ],
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

  const expected = {
    account_id: '1234',
    sk: 'ACCOUNT#1234'
  };

  expect(result).toContainEqual(expected);
});
