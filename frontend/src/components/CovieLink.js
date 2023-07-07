import { useEffect } from 'react';
import { API, Logger } from 'aws-amplify';
import { Button, Flex } from '@aws-amplify/ui-react';

const logger = new Logger('Covie');

export default function CovieLink() {

  useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://access.covie.io/sdk/covie-access.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    }
  }, []);

  return (
    <div>
      <div id="covie-root"></div>
      <script>
        window.covieReady = function() {
        window.Covie.access.button({
          elementId: 'covie-root',
          buttonTheme: 'covie',
          buttonText: 'Link Insurance',
          embed: { integrationKey: 'ik_emx55cdek5xtz2ro', linkId: '', metadata: {}, hide: [] },
        })
      }
      </script>
    </div>
  );
}
