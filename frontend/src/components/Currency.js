
export default function Currency({ amount, currency = 'USD' }) {
  if (!amount) {
    return '-';
  }

  const formatter = new Intl.NumberFormat(
    'en-US', { style: 'currency', currency, currencyDisplay: 'narrowSymbol'}
  );
  return formatter.format(amount);
}
