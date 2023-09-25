import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { useAuthenticator } from '@aws-amplify/ui-react';
import EmailBanner from './EmailBanner';

const logger = new Logger('Plaid');
const apiName = 'plaidapi';

export default function EmailGenerator({ plaidRequired, plaidUserToken, covieRequired, coviePolicies, sendEmail, emailSent, setEmailSent }) {
  // State to track request variables.
  const [emailRequest, setEmailRequest] = useState(true);

  // Get the user email.
  const { user } = useAuthenticator((context) => [context.user]);
  const email = user.signInUserSession.idToken.payload.email;

  // When the form is submitted, open the link.
  useEffect(() => {
    if (sendEmail && emailRequest) {
      sendEmailRequest();
    }
  }, [emailRequest]);

  // Sends the POST request to generate the email.
  const sendEmailRequest = async () => {
    // Get the POST response and log it.
    var requestBody = {
      email: email,
    };
    if (plaidRequired) {
      requestBody['plaidUserToken'] = plaidUserToken;
    }
    if (covieRequired) {
      requestBody['coviePolicies'] = coviePolicies;
    }
    try {
      const res = await API.get(apiName, '/v1/tokens/send-email', {
        body: requestBody,
      });
      logger.debug('POST /v1/tokens/send-email response:', res);
      // Set user ID and token values asynchronously.
    } catch (err) {
      logger.error('Unable to create link token:', err);
    }
    setEmailRequest(false);
    setEmailSent(true);
  };

  return emailSent ? <EmailBanner email={email} /> : null;
}
