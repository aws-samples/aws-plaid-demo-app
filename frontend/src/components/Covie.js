import { useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';

const logger = new Logger('Covie');

function printCovie(linkId, policies) {
  console.log(linkId);
  console.log(policies);
  setState(linkId, policies);
}

function setState(linkId, policies) {
  setLinkId(linkId);
  setPolicyIds(policies);
}

export default function Covie() {
  // Get lawyer's email to send data to.
  const { user } = useAuthenticator((context) => [context.user]);
  const userEmail = user.signInUserSession.idToken.payload.email;

  // State to track Plaid variables.
  const [linkId, setLinkId] = useState(null);
  const [policyIds, setPolicyIds] = useState(null);

  // Establish the link button. This code was provided by Covie.
  useEffect(() => {
    window.covieReady = function () {
      ' ';
    };
    {
      window.Covie.access.button({
        elementId: 'covie-root',
        buttonTheme: 'covie',
        buttonText: 'Link Insurance',
        embed: {
          integrationKey: 'ik_emx55cdek5xtz2ro',
          linkId: '',
          metadata: {},
          hide: [],
          onSuccess: printCovie,
        },
      });
    }
  }, []);

  return (
    <div>
      <div id="covie-root" />
    </div>
  );
}
