import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import OnboardingForm from '../components/Onboarding/OnboardingForm';
import OnboardingLink from '../components/Onboarding/OnboardingLink';
import EmailGenerator from '../components/Onboarding/EmailGenerator';

export default function Protected() {
  // State associated with form building.
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formOpen, setFormOpen] = useState(true);

  // State associated wtih link handling.
  const [linkOpen, setLinkOpen] = useState(false);
  // State associated with email sending.
  const [emailSent, setEmailSent] = useState(false);

  // State shared between form building and read by link handling.
  const [plaidToggle, setPlaidToggle] = useState(true);
  const [plaidNumber, setPlaidNumber] = useState(1);
  const [covieToggle, setCovieToggle] = useState(true);

  // When the form is submitted, open the link.
  useEffect(() => {
    if (formSubmitted) {
      setLinkOpen(true);
      setFormSubmitted(false);
    }
  }, [formSubmitted]);

  // State needed to generate the Plaid email.
  const [plaidUserToken, setPlaidUserToken] = useState(null);
  const [plaidRequired, setPlaidRequired] = useState(false);

  // State needed to generate the Plaid email.
  const [coviePolicies, setCoviePolicies] = useState(false);
  const [covieRequired, setCovieRequired] = useState(false);

  return (
    <Flex direction="column">
      <OnboardingForm
        plaidToggle={plaidToggle}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
        setPlaidRequired={setPlaidRequired}
        covieToggle={covieToggle}
        setCovieToggle={setCovieToggle}
        setCovieRequired={setCovieRequired}
        formSubmitted={formSubmitted}
        setFormSubmitted={setFormSubmitted}
      />

      <OnboardingLink
        open={linkOpen}
        setOpen={setLinkOpen}
        plaidToggle={plaidToggle}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
        plaidUserToken={plaidUserToken}
        setPlaidUserToken={setPlaidUserToken}
        covieToggle={covieToggle}
        setCovieToggle={setCovieToggle}
        setCoviePolicies={setCoviePolicies}
      />

      <EmailGenerator/>
    </Flex>
  );
}
