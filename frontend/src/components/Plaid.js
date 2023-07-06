import { useEffect, useState } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';
import PlaidLink from './PlaidLink';

const logger = new Logger('Plaid');

const apiName = 'plaidapi';
const TEST_CLIENT_USER_ID = 'test1';

export default function Plaid() {
  const [connecting, setConnecting] = useState(false);
  const [user_id, setUserId] = useState(null);
  const [user_token, setUserToken] = useState(null);
  const [employment_verification_token, setEmploymentVerificationToken] = useState(null);
  const [payroll_income_token, setPayrollIncomeToken] = useState(null);

  const handleGetEmploymentVerificationToken = async () => {
    setConnecting(true);
    // TODO: Make the async chained.
    var userId;
    var userToken;

    // Create the user token.
    try {
      const res = await API.post(apiName, '/v1/tokens/user', {
        body: {
          client_user_id: TEST_CLIENT_USER_ID,
        },
      });
      logger.debug('POST /v1/tokens/user response:', res);
      setUserId(res.user_id);
      userId = res.user_id;
      setUserToken(res.user_token);
      userToken = res.user_token;
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
    // Create the employment verification link.
    try {
      const res = await API.post(apiName, '/v1/tokens/link-employment', {
        body: {
          client_user_id: TEST_CLIENT_USER_ID,
          user_token: userToken
        },
      });
      logger.debug('POST /v1/tokens/link-employment response:', res);
      setEmploymentVerificationToken(res.link_token);
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  };

  const handleEmploymentVerificationSuccess = async () => {
    // Create the employment verification link.
    try {
      const res = await API.post(apiName, '/v1/tokens/link-payroll', {
        body: {
          client_user_id: TEST_CLIENT_USER_ID,
          user_token: user_token
        },
      });
      logger.debug('POST /v1/tokens/link-payroll response:', res);
      setPayrollIncomeToken(res.link_token);
    } catch (err) {
      logger.error('unable to create link token:', err);
    }
  }

  const handlePayrollIncomeSuccess = async () => {
      try {
        const res = await API.post(apiName, '/v1/tokens/payroll', {
          body: {
            user_token: user_token,
          },
        });
        logger.debug('POST /v1/payroll response:', res);
      } catch (err) {
        logger.error('unable to get payroll information', err);
      }
      setConnecting(false);
    };

  return (
    <Flex>
      <Button variation="primary" isLoading={connecting} onClick={handleGetEmploymentVerificationToken}>
        CONNECT WITH PLAID
      </Button>
      {employment_verification_token ? (
        <PlaidLink token={employment_verification_token} onSuccess={handleEmploymentVerificationSuccess} onExit={() => setConnecting(false)} />
      ) : null}
      {payroll_income_token ? (
        <PlaidLink token={payroll_income_token} onSuccess={handlePayrollIncomeSuccess} onExit={() => setConnecting(false)} />
      ) : null}
    </Flex>
  );
}
