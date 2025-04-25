
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

export const getTransactions = `query GetTransactions($id: ID!, $limit: Int, $cursor: String) {
  getTransactions(id: $id, limit: $limit, cursor: $cursor) {
    transactions {
      transaction_id
      account_id
      name
      amount
      iso_currency_code
      payment_channel
      transaction_type
      date
    }
    cursor
  }
}`;

export const getInvestmentAccounts = `query GetInvestmentAccounts($id: ID!) {
  getInvestmentAccounts(id: $id) {
    account_id
    name
    type
    balances {
      current
      iso_currency_code
      available
    }
    subtype
    mask
  }
}`;

export const getInvestmentHoldings = `query GetInvestmentHoldings($id: ID!) {
  getInvestmentHoldings(id: $id) {
    account_id
    security_id
    institution_price
    institution_price_as_of
    cost_basis
    quantity
    currency
    security {
      security_id
      ticker_symbol
      name
      currency
      type
    }
  }
}`;

export const disconnectItem = `mutation DisconnectItem($id: ID!) {
  disconnectItem(id: $id)
}`;
