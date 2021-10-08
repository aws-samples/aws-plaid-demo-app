const aws = require('aws-sdk')
var express = require('express')
var bodyParser = require('body-parser')
var awsServerlessExpressMiddleware = require('aws-serverless-express/middleware')
const Plaid = require('plaid')
const moment = require('moment');

aws.config.update({ region: process.env.TABLE_REGION });
const dynamodb = new aws.DynamoDB.DocumentClient();

// declare a new express app
var app = express()
app.use(bodyParser.json())
app.use(awsServerlessExpressMiddleware.eventContext())

const client = async () => {
  const { Parameters } = await (new aws.SSM())
    .getParameters({
      Names: ["PLAID_SECRET"].map(secretName => process.env[secretName]),
      WithDecryption: true,
    })
    .promise();
  const clientID = process.env.CLIENT_ID;

  const secret = Parameters.pop().Value;

  const ret = new Plaid.Client({
    env: Plaid.environments.sandbox,
    clientID,
    secret,
  });

  return ret;
};

// Enable CORS for all methods
app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*")
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
  next()
});

app.get('/v1/token', async function (req, res) {
  try {
    const cl = await client();
    try {
      const resp = await cl.createLinkToken({
        user: {
          client_user_id: req.query.sub,
        },
        client_name: 'plaidaws',
        products: ['transactions'],
        country_codes: ['US'],
        language: 'en',
      });
      res.json({ token: resp.link_token });

    } catch (err) {
      res.json({ token: err });
    }
  } catch (clienterr) {
    console.log(`client error ----> ${JSON.stringify(clienterr)}`);
  }
});

app.get('/v1/transactions', async function (req, res) {
  const cl = await client();
  const tableName = process.env.TABLE_NAME + "-dev";
  const params = {
    TableName: tableName,
    Key: {
      id: req.query.sub,
    },
  };

  let startDate = moment()
    .subtract(30, "days")
    .format("YYYY-MM-DD");

  let endDate = moment().format("YYYY-MM-DD");

  dynamodb.get(params, (err, data) => {
    if (err) {
      res.statusCode = 500;
      return res.json({ err });
    } else {
      if (data.Item) {
        const { token } = data.Item;
        cl.getTransactions(token, startDate, endDate, {
          count: 250,
          offset: 0
        }, (error, transResp) => {
          res.json({ msg: transResp.transactions });
        });
      } else {
        res.json({ msg: [] });
      }
    }
  });
});

app.post('/v1/token', async function (req, res) {
  const { token, sub } = req.body;
  const cl = await client();
  cl.exchangePublicToken(token, (error, resp) => {
    if (error != null) {
      return res.json({error});
    } else {

      const tableName = process.env.TABLE_NAME + "-dev";
      const putItemParams = {
        TableName: tableName,
        Item: {
          id: sub,
          token: resp.access_token,
        },
      };

      dynamodb.put(putItemParams, (err, data) => {
        if (err) {
          res.statusCode = 500;
          res.json({ err, url: req.url, body: req.body });
        } else {
          res.json({success: 'post call succeed!', url: req.url, body: req.body, data: data});
        }
      });
    }
  });
});
app.listen(3000, function () {
  console.log("App started")
});

// Export the app object. When executing the application local this does nothing. However,
// to port it to AWS Lambda we will create a wrapper around that will load the app from
// this file
module.exports = app

