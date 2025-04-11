import { Authenticator, Image } from '@aws-amplify/ui-react';
import { useAuthenticator, View, Heading, Text, Flex } from '@aws-amplify/ui-react';
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router';

export default function Login() {
  const { route } = useAuthenticator((context) => [context.route]);
  const location = useLocation();
  const navigate = useNavigate();
  let from = location.state?.from?.pathname || '/';

  const components = {
    Header() {
      return (
        <Flex direction="column" alignItems="center">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginBottom: '1rem', color: 'var(--color-primary-main)' }}>
            <path d="M3 13.125C3 12.5727 3.44772 12.125 4 12.125H6C6.55228 12.125 7 12.5727 7 13.125V20C7 20.5523 6.55228 21 6 21H4C3.44772 21 3 20.5523 3 20V13.125Z" fill="currentColor"/>
            <path d="M10 8.125C10 7.57272 10.4477 7.125 11 7.125H13C13.5523 7.125 14 7.57272 14 8.125V20C14 20.5523 13.5523 21 13 21H11C10.4477 21 10 20.5523 10 20V8.125Z" fill="currentColor"/>
            <path d="M17 3.125C17 2.57272 17.4477 2.125 18 2.125H20C20.5523 2.125 21 2.57272 21 3.125V20C21 20.5523 20.5523 21 20 21H18C17.4477 21 17 20.5523 17 20V3.125Z" fill="currentColor"/>
          </svg>
          <Heading level={4} className="auth-title">
            Passive Analytics
          </Heading>
          <Text className="auth-subtitle">
            Sign in to access your financial dashboard
          </Text>
        </Flex>
      );
    },
    Footer() {
      return (
        <Text
          fontSize="0.8rem"
          color="var(--color-text-tertiary)"
          textAlign="center"
          padding="1rem"
        >
          By signing in you agree to our Terms of Service and Privacy Policy.
        </Text>
      );
    },
    SignUp: {
      Header() {
        return (
          <Flex direction="column" alignItems="center">
            <Heading level={4} className="auth-title">
              Create an account
            </Heading>
            <Text className="auth-subtitle">
              Track and analyze your investments
            </Text>
          </Flex>
        );
      },
      Footer() {
        return (
          <View textAlign="left" padding="1rem" backgroundColor="var(--color-bg-tertiary)" borderRadius="8px" marginTop="1.5rem">
            <Text fontWeight="600" marginBottom="0.5rem">Password Requirements:</Text>
            <ul style={{ paddingLeft: '1.5rem', margin: '0.5rem 0' }}>
              <li>Minimum of 8 characters</li>
              <li>At least one lowercase character</li>
              <li>At least one uppercase character</li>
              <li>At least one number</li>
              <li>At least one special character</li>
            </ul>
          </View>
        );
      }
    }
  };

  useEffect(() => {
    if (route === 'authenticated') {
      navigate(from, { replace: true });
    }
  }, [route, navigate, from]);

  return (
    <View className="auth-wrapper">
      <View className="auth-container">
        <Authenticator 
          components={components}
          loginMechanisms={['email']}
          variation="modal"
          hideSignUp={false}
        />
      </View>
    </View>
  );
}
