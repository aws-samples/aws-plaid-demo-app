import { useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';

const logger = new Logger('Covie');

function test(e, n) {
  console.log(e);
  console.log(n);
}

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
          onSuccess: function(e,n){console.log(n)}, 
        },
      });
    };
  }, []);

  return (
    <div>
      <div id="covie-root" />
    </div>
  );
}
