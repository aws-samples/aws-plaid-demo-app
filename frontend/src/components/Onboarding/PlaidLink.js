import { useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';

export default function PlaidLink({ token, onSuccess, onExit }) {
  const { open, ready, error } = usePlaidLink({
    token,
    onSuccess,
    onExit,
  });

  useEffect(() => {
    if (token) {
      open();
    }
  }, [token, open]);

  return <div />;
}
