
export const getItems = `query GetItems($limit: Int, $cursor: String) {
  getItems(limit: $limit, cursor: $cursor) {
    items {
      item_id
      institution_id
      institution_name
    }
    cursor
  }
}`;

export const getAccounts = `query GetAccounts($id: ID!) {
  getAccounts(id: $id) {
    account_id
    name
    type
    balances {
      current
      iso_currency_code
    }
    subtype
    mask
  }
}`;

export const getInvestmentAccounts = `query GetInvestmentAccounts($id: ID!) {
  getInvestmentAccounts(id: $id) {
    account_id
    name
    type
    subtype
    balances {
      current
      iso_currency_code
    }
    mask
  }
}`;

export const getInvestmentHoldings = `query GetInvestmentHoldings($accountId: ID!) {
  getInvestmentHoldings(accountId: $accountId) {
    account_id
    security_id
    quantity
    cost_basis
    institution_value
    iso_currency_code
    security {
      security_id
      name
      ticker_symbol
      type
      close_price
      close_price_as_of
      iso_currency_code
    }
  }
}`;

export const getInvestmentTransactions = `query GetInvestmentTransactions($accountId: ID!, $limit: Int, $cursor: String) {
  getInvestmentTransactions(accountId: $accountId, limit: $limit, cursor: $cursor) {
    investment_transactions {
      investment_transaction_id
      account_id
      security_id
      date
      name
      quantity
      amount
      price
      fees
      type
      iso_currency_code
      security {
        security_id
        name
        ticker_symbol
        type
      }
    }
    cursor
  }
}`;
