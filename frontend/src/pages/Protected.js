import { useState, useEffect } from 'react';
import { Logger } from 'aws-amplify';
import { Flex } from '@aws-amplify/ui-react';
import OnboardingForm from '../components/Onboarding/OnboardingForm';
import OnboardingLink from '../components/Onboarding/OnboardingLink';

export default function Protected() {
  // State associated with form building.
  const [formSubmitted, setFormSubmitted] = useState(false);
  // State associated wtih link handling.
  const [linkOpen, setLinkOpen] = useState(false);
  // State associated with email sending.
  const [sendEmail, setSendEmail] = useState(false);

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

  return (
    <Flex direction="column">
      <OnboardingForm
        plaidToggle={plaidToggle}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
        covieToggle={covieToggle}
        setCovieToggle={covieToggle}
        setFormSubmitted={setFormSubmitted}
      />

      <OnboardingLink
        open={linkOpen}
        setOpen={setLinkOpen}
        plaidToggle={plaidToggle}
        setPlaidToggle={setPlaidToggle}
        plaidNumber={plaidNumber}
        setPlaidNumber={setPlaidNumber}
        covieToggle={covieToggle}
        setCovieToggle={covieToggle}
      />
    </Flex>
  );
}
