from plaid.model.processor_stripe_bank_account_token_create_request import ProcessorStripeBankAccountTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import plaid
from plaid.api import plaid_api
from plaid.model.depository_account_subtypes import DepositoryAccountSubtypes
from plaid.model.depository_account_subtype import DepositoryAccountSubtype
from plaid.model.country_code import CountryCode
from plaid.model.depository_filter import DepositoryFilter
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_auth import LinkTokenCreateRequestAuth
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_get_request import LinkTokenGetRequest
from plaid.model.products import Products
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from .config import PLAID_CLIENT_ID, PLAID_SECRET

# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)


api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


request = LinkTokenCreateRequest(
    products=[Products('auth'), Products('transactions')],
    client_name="Plaid Test App",
    country_codes=[CountryCode('US')],
    redirect_uri='https://domainname.com/oauth-page.html',
    language='en',
    webhook='https://sample-webhook-uri.com',
    link_customization_name='default',
    account_filters=LinkTokenAccountFilters(
        depository=DepositoryFilter(
            account_subtypes=DepositoryAccountSubtypes(
                [DepositoryAccountSubtype(
                    'checking'), DepositoryAccountSubtype('savings')]
            )
        )
    ),
    user=LinkTokenCreateRequestUser(
        client_user_id=PLAID_CLIENT_ID
    ),
)
response = client.link_token_create(request)

public_token = ""

# create link token
response = client.link_token_create(request)
link_token = response['link_token']

# public token exchanged for access token
request = ItemPublicTokenExchangeRequest(public_token=public_token)
response = client.item_public_token_exchange(request)
access_token = response['access_token']
item_id = response['item_id']

request = AccountsBalanceGetRequest(access_token=access_token)
response = client.accounts_balance_get(request)
accounts = response['accounts']
