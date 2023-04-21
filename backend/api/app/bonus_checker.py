import boto3
import botocore
from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table
from datetime import datetime, timedelta
from .config import TABLE_NAME, AWS_SERVER_PUBLIC_KEY, AWS_SERVER_SECRET_KEY
from app import constants
from logging import Logger
logger = Logger(child=True)

dynamodb = boto3.resource("dynamodb", region_name='us-west-1',
                          aws_access_key_id=AWS_SERVER_PUBLIC_KEY, aws_secret_access_key=AWS_SERVER_SECRET_KEY)
table = dynamodb.Table(TABLE_NAME)
dynamodb_client = dynamodb.meta.client


'''
CHECKER_DATA = {
    "CitiBank": [
        {
            "account_type": {
                "names": ["business checking account in-branch"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-07-12"
                },
                "contraint_or": [{
                    "amount_within_days": 30,
                    "amount_greater": 5000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 15000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 25000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 50000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 100000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 200000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 200
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 700
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1000
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 2000
                }],
                "info": {
                    "amount_credit": "within 90 days from the end of the month"
                }
            }
            ]
        },
        {
            "account_type": {
                "names": ["Priority Account"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-07-23"
                },
                "contraint_or": [{
                    "amount_within_days": 20,
                    "amount_greater": 10000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 30000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 75000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 200000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 300000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "after_days": 21,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 200
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1000
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 2000
                }],
                "info": {
                    "amount_credit": "within 30 calendar days after completing the requirements"
                }
            }
            ]
        }
    ],
    "U.S. Bank": [
        {
            "account_type": {
                "name": ["Business Checking"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-04-23"
                },
                "contraint_or": [{
                    "amount_within_days": 60,
                    "amount_greater": 3000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "after_days": None,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": 45,
                    "credit_after_date": None,
                    "amount": 500
                }]
            }]
        },
        {
            "account_type": {
                "name": ["Standard Savings Account"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-05-02"
                },
                "contraint_or": [{
                    "amount_within_days": None,
                    "amount_within_date": "2023-05-31",
                    "amount_greater": 15000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": None,
                    "after_days": None,
                    "for_date": "2023-08-31",
                    "minimum_balance": 25000,
                },
                "bonuses": [{
                    "credit_after_days": 30,
                    "credit_after_date": None,
                    "amount": 200
                }]
            }]
        }, {
            "account_type": {
                "name": ["Smartly checking account"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-05-02"
                },
                "contraint_or": [{
                    "amount_within_days": 90,
                    "amount_within_date": None,
                    "amount_greater": 5000,
                    "no_of_recurring_deposits": 2,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": None,
                    "after_days": None,
                    "for_date": None,
                    "minimum_balance": None,
                },
                "bonuses": [{
                    "credit_after_days": 60,
                    "credit_after_date": None,
                    "amount": 200
                }]
            }]
        },
    ]
}
'''

CHECKER_DATA = {
    "CitiBank": [
        {
            "account_type": {
                "names": ["Plaid Bronze Standard 0.2% Interest CD"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-07-12"
                },
                "contraint_or": [{
                    "amount_within_days": 30,
                    "amount_greater": 500,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 1500,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 2500,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 5000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 10000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 30,
                    "amount_greater": 20000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 200
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 700
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1000
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 2000
                }],
                "info": {
                    "amount_credit": "within 90 days from the end of the month"
                }
            }
            ]
        },
        {
            "account_type": {
                "names": ["Plaid Diamond 12.5% APR Interest Credit Card"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-07-23"
                },
                "contraint_or": [{
                    "amount_within_days": 20,
                    "amount_greater": 1000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 3000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 7500,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 20000,
                    "amount_less": None,
                    "amount_equals": None
                }, {
                    "amount_within_days": 20,
                    "amount_greater": 30000,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "after_days": 21,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 200
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1000
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 1500
                }, {
                    "credit_after_days": "info",
                    "credit_after_date": "info",
                    "amount": 2000
                }],
                "info": {
                    "amount_credit": "within 30 calendar days after completing the requirements"
                }
            }
            ]
        }
    ],
    "U.S. Bank": [
        {
            "account_type": {
                "names": ["Plaid Gold Standard 0% Interest Checking"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-04-23"
                },
                "contraint_or": [{
                    "amount_within_days": 60,
                    "amount_greater": 300,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": 60,
                    "after_days": None,
                    "for_date": None,
                    "minimum_balance": "same",
                },
                "bonuses": [{
                    "credit_after_days": 45,
                    "credit_after_date": None,
                    "amount": 500
                }]
            }]
        },
        {
            "account_type": {
                "names": ["Plaid Platinum Standard 1.85% Interest Money Market"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-05-02"
                },
                "contraint_or": [{
                    "amount_within_days": None,
                    "amount_within_date": "2023-05-31",
                    "amount_greater": 1500,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": None,
                    "after_days": None,
                    "for_date": "2023-08-31",
                    "minimum_balance": 2500,
                },
                "bonuses": [{
                    "credit_after_days": 30,
                    "credit_after_date": None,
                    "amount": 200
                }]
            }]
        },
        {
            "account_type": {
                "names": ["Plaid Silver Standard 0.1% Interest Saving"]
            },
            "conditions": [{
                "start": {
                    "date": None,
                },
                "expiry": {
                    "date": "2023-05-02"
                },
                "contraint_or": [{
                    "amount_within_days": 90,
                    "amount_within_date": None,
                    "amount_greater": 500,
                    "no_of_recurring_deposits": 2,
                    "amount_less": None,
                    "amount_equals": None
                }],
                "maintain": {
                    "for_days": None,
                    "after_days": None,
                    "for_date": None,
                    "minimum_balance": None,
                },
                "bonuses": [{
                    "credit_after_days": 60,
                    "credit_after_date": None,
                    "amount": 200
                }]
            }]
        },
    ]
}

# ACCOUNT_TYPES = ['Plaid Bronze Standard 0.2% Interest CD', 'Plaid Diamond 12.5% APR Interest Credit Card', 'Plaid Gold Standard 0% Interest Checking',
#                  'Plaid Platinum Standard 1.85% Interest Money Market', 'Plaid Silver Standard 0.1% Interest Saving']


class UserAccountBankCheck:
    def __init__(self, transactions, conditions):
        self.transactions = transactions
        self.conditions = conditions
        self.amount_to_check = -1

    def check_maintain_conditions(self):
        maintain_data = self.conditions.get("maintain")
        account_open_date = self.transactions[0].get("updated_at")
        till_date = datetime.strptime(
            account_open_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=maintain_data.get("for_days"))
        for transaction in self.transactions:
            if maintain_data.get("minimum_balance") == "same" and till_date >= datetime.strptime(
                    transaction.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ"):
                return True
            elif maintain_data.get("minimum_balance") <= self.amount_to_check:
                return True
        return False

    def check_start_conditions(self):
        start_date = self.conditions.get("start").get('date', None)
        if start_date:
            return datetime.strptime(start_date, "%Y-%m-%d") < datetime.now()
        return True

    def check_expiry_conditions(self):
        expiry_date = self.conditions.get("expiry").get('date', None)
        if expiry_date:
            return datetime.strptime(expiry_date, "%Y-%m-%d") > datetime.now()
        return True

    def check_constraint_conditions(self):
        contraint_or = self.conditions.get("contraint_or")
        for transaction in self.transactions:
            index = -1
            for contraint in contraint_or:
                balance = transaction.get("balances")
                current_balance = balance.get("current")
                if current_balance >= contraint.get("amount_greater"):
                    self.amount_to_check = contraint.get("amount_greater")
                    index += 1
                else:
                    break
            if index != -1:
                return index
        return -1

    def get_bonus(self, index):
        return self.conditions.get("bonuses")[index]


class FormatAccountData:
    def __init__(self):
        self.transaction_data = None

    def get_all_accounts_type(self, data, key):
        self.transaction_data = list(filter(lambda d: d.get('official_name') ==
                                            key, data))

    def get_unique_accounts(self):
        unique_accounts = set()
        for account in self.transaction_data:
            unique_accounts.add(account.get('account_id'))
        return list(unique_accounts)

    def sort_transaction_by_date(self, data):
        data.sort(key=lambda x: datetime.strptime(
            x['updated_at'], "%Y-%m-%dT%H:%M:%SZ"))
        return data

    def get_all_account_data(self, account):
        return list(filter(lambda d: d.get('account_id') ==
                           account, self.transaction_data))


def fetch_transactions_data():
    response = table.scan()
    data = response['Items']
    return data


def bonus_checker():
    try:
        all_transactions_data = fetch_transactions_data()
        for bank in CHECKER_DATA.keys():
            bank_conditions = CHECKER_DATA.get(bank)
            for bank_condition in bank_conditions:
                format_data = FormatAccountData()
                format_data.get_all_accounts_type(all_transactions_data, bank_condition.get(
                    "account_type").get("names")[0])
                unique_accounts = format_data.get_unique_accounts()
                print(unique_accounts)
                for account in unique_accounts:
                    account_data = format_data.get_all_account_data(account)
                    sorted_account_data = format_data.sort_transaction_by_date(
                        account_data)
                    # print(sorted_account_data)
                    bank_check = UserAccountBankCheck(
                        sorted_account_data, bank_condition.get("conditions")[0])
                    start_condition = bank_check.check_start_conditions()
                    expiry_condition = bank_check.check_expiry_conditions()
                    constraint_condition_index = bank_check.check_constraint_conditions()
                    maintain_condition = bank_check.check_maintain_conditions()
                    if constraint_condition_index != -1:
                        print(account, "won bonus", bank_check.get_bonus(
                            constraint_condition_index).get("amount"))
                    break
                break
            break
    except botocore.exceptions.ClientError:
        logger.exception("Unable to get items from DynamoDB")
        raise
