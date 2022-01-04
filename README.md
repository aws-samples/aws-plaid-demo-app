# AWS Plaid Demo App

This repo demonstrates how to build a Fintech app on AWS that uses Plaid Link to connect a user to his or her bank 
account. The app allows users to sign up using Amazon Cognito, select their bank from a list, log in to the bank, and display the latest transactions. The app is built using AWS Amplify, Amazon API Gateway, Amazon Cognitio, AWS Secrets 
Manager and Amazon DynamoDB. 

## Pre-requisites
Before building the app, you will need to get your API keys from Plaid. Go to https://plaid.com, click on the **Get API Keys** button, and create an account. You can create a free sandbox account, and use your sandbox API key to start.

Install AWS Amplify by following the instructions at https://docs.amplify.aws/cli/start/install/ 

If you have not already done so, create a default AWS configuration profile by running the **aws configure** command, as described at https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config 

## Building the app 

```
$ git clone https://github.com/aws-samples/aws-plaid-demo-app
$ cd aws-plaid-demo-app
$ npm install

```

Then perform the following steps. 

1. Initialize a new amplify project.

### `amplify init`

```
? Enter a name for the project (awsplaiddemoapp)
? Initialize the project with the above configuration? (Y/n) y
? Select the authentication profile you want to use: AWS profile 
? Please choose the profile you want to use: default
```
2. Add Authentication.

### `amplify add auth`
```
? Do you want to use the default authentication configuration? Default configuration 
? How do you want users to be able to sign in? (Use arrow keys and space bar to select)
•	Email
•	Username
? Do you want to configure advanced settings? No, I am done
```

3. Add the API.

### `amplify add api`

Follow these steps after for API creation

```
? Please select from one of the below mentioned services: REST
? Would you like to add a new path to an existing REST API: No
? Provide a friendly name for your resource to be used as a label for this category in the project: plaidtestapi
? Provide a path (e.g., /book/{isbn}): /v1
? Choose a Lambda source Create a new Lambda function
? Provide an AWS Lambda function name: plaidaws
? Choose the runtime that you want to use: NodeJS
? Choose the function template that you want to use: Serverless ExpressJS function (Integration with API Gateway)

Available advanced settings:
- Resource access permissions
- Scheduled recurring invocation
- Lambda layers configuration
- Environment variables configuration
- Secret values configuration

? Do you want to configure advanced settings? Yes
? Do you want to access other resources in this project from your Lambda function? No
? Do you want to invoke this function on a recurring schedule? No
? Do you want to enable Lambda layers for this function? No
? Do you want to configure environment variables for this function? Yes
? Enter the environment variable name: CLIENT_ID
? Enter the environment variable value: [Enter your Plaid client ID]
? Select what you want to do with environment variables: Add new environment variable
? Enter the environment variable name: TABLE_NAME
? Enter the environment variable value: plaidawsdb
? Select what you want to do with environment variables: I'm done


You can access the following resource attributes as environment variables from your Lambda function
	ENV
	REGION
	CLIENT_ID
	TABLE_NAME

? Do you want to configure secret values this function can access? Yes
? Enter a secret name (this is the key used to look up the secret value): PLAID_SECRET
? Enter the value for PLAID_SECRET: [Enter your Plaid sandbox API key - hidden]
? What do you want to do? I'm done
? Do you want to edit the local lambda function now? No
? Press enter to continue
Successfully added resource plaidaws locally.
? Restrict API access No
? Do you want to add another path? No
Successfully added resource plaidtestapi locally
```

Copy the lambda function file

`cp lambda/plaidaws/app.js amplify/backend/function/plaidaws/src/app.js`

Next `cd` into our lambda function's directory

`cd amplify/backend/function/plaidaws/src`

install some dependencies we're going to be using

`npm i aws-sdk moment plaid@8.5.4`


4. `amplify push`

5. Add Storage. 

### `amplify add storage`

```
? Please select from one of the below mentioned services: NoSQL Database

Welcome to the NoSQL DynamoDB database wizard
This wizard asks you a series of questions to help determine how to set up your NoSQL database table.

? Please provide a friendly name for your resource that will be used to label this category in the project: plaidawsdb

The table name must be the same as the value of the TABLE_NAME environment variable above 

? Please provide table name: plaidawsdb

You can now add columns to the table.

? What would you like to name this column: id
? Please choose the data type: string
? Would you like to add another column? Yes
? What would you like to name this column: token
? Please choose the data type: string
? Would you like to add another column? No

Before you create the database, you must specify how items in your table are uniquely organized. You do this by specifying a primary key. The primary key uniquely identifies each item in the table so that no two items can have the same key. This can be an individual column, or a combination that includes a primary key and a sort key.

To learn more about primary keys, see:
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey

? Please choose partition key for the table: id
? Do you want to add a sort key to your table? No

You can optionally add global secondary indexes for this table. These are useful when you run queries defined in a different column than the primary key.
To learn more about indexes, see:
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.SecondaryIndexes

? Do you want to add global secondary indexes to your table? No
? Do you want to add a Lambda Trigger for your Table? No
Successfully added resource plaidawsdb locally
```

6. Update our Lambda function to add permissions for database.

### `amplify update function`

```
? Select the Lambda function you want to update plaidaws
General information
- Name: plaidaws
- Runtime: nodejs

Resource access permission
- Not configured

Scheduled recurring invocation
- Not configured

Lambda layers
- Not configured

Environment variables:
- CLIENT_ID: plaidclientid

Secrets configuration
- PLAID_SECRET

? Which setting do you want to update? Resource access permissions
? Select the categories you want this function to have access to. storage
? Storage has 2 resources in this project. Select the one you would like your La
mbda to access plaidtestdb
? Select the operations you want to permit on plaidtestdb create, read, update,
delete

You can access the following resource attributes as environment variables from your Lambda function
	STORAGE_PLAIDTESTDB_ARN
	STORAGE_PLAIDTESTDB_NAME
	STORAGE_PLAIDTESTDB_STREAMARN
? Do you want to edit the local lambda function now? No
```

7. Add Hosting to deploy the site.

### `amplify add hosting`

? Select the plugin module to execute: Hosting with Amplify Console (Managed hosting)
? Choose a type: Manual deployment


8. Publish the site.

### `amplify publish`

## Testing the app

Go to the URL displayed by the amplify publish command, and sign up as a new user. After logging in, select a bank from the list displayed. If you are using the sandbox environment, use the credentials **user_good / pass_good** to access the bank and display the transactions.

