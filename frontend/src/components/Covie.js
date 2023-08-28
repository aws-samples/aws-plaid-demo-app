import { useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';

const logger = new Logger('Covie');

export default function Covie() {
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
          onSuccess: (linkId, policies) => {
            console.log(linkId);
            console.log(policies);
          },
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
