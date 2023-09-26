import { createRoot } from 'react-dom/client';
import { Amplify, Auth } from "aws-amplify";
import App from './App';

import '@aws-amplify/ui-react/styles.css';
import '@fontsource/inter/variable.css';
import "./index.css";

const container = document.getElementById('root');
const root = createRoot(container);

Amplify.Logger.LOG_LEVEL = 'DEBUG';

// Try to dynamically import aws-exports
import('./aws-exports')
  .then(awsconfig => {
    // If aws-exports.js is available
    Amplify.configure(awsconfig.default);
  })
  .catch(err => {
    // If aws-exports.js is NOT available, use the old settings
    Amplify.configure({
      aws_appsync_graphqlEndpoint: process.env.REACT_APP_GRAPHQL_URL,
      aws_appsync_region: process.env.REACT_APP_REGION,
      aws_appsync_authenticationType: 'AMAZON_COGNITO_USER_POOLS',
      Auth: {
        region: process.env.REACT_APP_REGION,
        userPoolId: process.env.REACT_APP_COGNTIO_USERPOOL_ID,
        userPoolWebClientId: process.env.REACT_APP_COGNITO_CLIENT_ID,
        mandatorySignIn: true,
        oauth: {
          domain: process.env.REACT_APP_COGNITO_DOMAIN,
          scope: ['email', 'openid', `${process.env.REACT_APP_BACKEND_URL}/plaid.rw}`],
          responseType: 'code'
        }
      },
      API: {
        endpoints: [
          {
            name: "plaidapi",
            endpoint: process.env.REACT_APP_BACKEND_URL,
            region: process.env.REACT_APP_REGION,
            clientId: process.env.REACT_APP_COGNITO_CLIENT_ID,
            custom_header: async () => {
              return { Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}` }
            }
          }
        ]
      }
    });
  })
  .finally(() => {
    root.render(<App />);
  });
