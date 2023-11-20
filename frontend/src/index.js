import { createRoot } from 'react-dom/client';
import { Amplify } from "aws-amplify";
import { ConsoleLogger } from "aws-amplify/utils";
import { fetchAuthSession } from "aws-amplify/auth";
import App from './App';

import '@aws-amplify/ui-react/styles.css';
import "@fontsource/inter";
import "./index.css";

const container = document.getElementById('root');
const root = createRoot(container);

ConsoleLogger.LOG_LEVEL = 'DEBUG';

const existingConfig = Amplify.getConfig();

async function custom_headers() {
  const accessToken  = (await fetchAuthSession()).tokens?.accessToken?.toString();
  return { Authorization: `Bearer ${accessToken}` }
}

const libraryOptions = {
  API: {
    GraphQL: {
      headers: custom_headers
    },
    REST: {
      headers: custom_headers
    }
  }
}

Amplify.configure({
  ...existingConfig,
  Auth: {
    ...existingConfig.Auth,
    Cognito: {
      ...existingConfig.Auth?.Cognito,
      userPoolId: process.env.REACT_APP_COGNTIO_USERPOOL_ID,
      userPoolClientId: process.env.REACT_APP_COGNITO_CLIENT_ID,
      signUpVerificationMethod: 'code',
      loginWith: {
        oauth: {
          domain: process.env.REACT_APP_COGNITO_DOMAIN,
          scopes: ['email', 'openid', `${process.env.REACT_APP_BACKEND_URL}/plaid.rw}`],
          responseType: 'code'
        }
      },
      mfa: {
        status: 'on'
      },
      passwordFormat: {
        requireNumbers: true,
        minLength: 8,
        requireLowercase: true,
        requireSpecialCharacters: true,
        requireUppercase: true
      },
    },
  },
  API: {
    ...existingConfig.API,
    GraphQL: {
      ...existingConfig.API?.GraphQL,
      endpoint: process.env.REACT_APP_GRAPHQL_URL,
      region: process.env.REACT_APP_REGION,
      defaultAuthMode: 'none',
    },
    REST: {
      ...existingConfig.API?.REST,
      plaidapi: {
        endpoint: process.env.REACT_APP_BACKEND_URL,
        region: process.env.REACT_APP_REGION,
      },
    },
  }
}, libraryOptions);

const config = Amplify.getConfig();
console.log('CONFIG:', config);

root.render(<App />);
