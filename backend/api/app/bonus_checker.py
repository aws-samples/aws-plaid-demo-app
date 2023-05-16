import boto3
import botocore
from datetime import datetime, timedelta
from .config import TABLE_NAME, AWS_SERVER_PUBLIC_KEY, AWS_SERVER_SECRET_KEY
import json
with open('CHECKER_DATA.json', 'r') as file:
    banks = json.load(file)

dynamodb = boto3.resource("dynamodb", region_name='us-west-1',
                          aws_access_key_id=AWS_SERVER_PUBLIC_KEY, aws_secret_access_key=AWS_SERVER_SECRET_KEY)
table = dynamodb.Table(TABLE_NAME)
dynamodb_client = dynamodb.meta.client

# ACCOUNT_TYPES = ['Plaid Bronze Standard 0.2% Interest CD', 'Plaid Diamond 12.5% APR Interest Credit Card', 'Plaid Gold Standard 0% Interest Checking',
#                  'Plaid Platinum Standard 1.85% Interest Money Market', 'Plaid Silver Standard 0.1% Interest Saving']

# Main User Bank account conditions matcher
class UserBankAccountCheck:
    DATA_FORMAT = "%Y-%m-%d"
    DATE_VALUE = "%Y-%m-%dT%H:%M:%SZ"
    def __init__(self, transactions, conditions):
        self.transactions = transactions
        self.conditions = conditions
        self.amount_to_check = -1

    def check_maintain_conditions(self):
        maintain_data = self.conditions.get("maintain")
        if maintain_data:
            try:
                account_open_date = self.transactions[0].get("updated_at")
                if maintain_data.get("for_days"):
                    till_date = datetime.strptime(account_open_date, self.DATE_VALUE) + timedelta(days=maintain_data.get("for_days"))
                elif maintain_data.get("for_date"):
                    till_date = datetime.strptime(maintain_data.get("for_date"), self.DATA_FORMAT)
                else:
                    till_date = datetime.strptime("2050-04-18", self.DATA_FORMAT)
                for transaction in self.transactions:
                    if maintain_data.get("minimum_balance"):
                        if maintain_data.get("minimum_balance") == "same" and till_date >= datetime.strptime(
                                transaction.get("updated_at"), self.DATE_VALUE):
                            return True
                        elif maintain_data.get("minimum_balance") <= self.amount_to_check:
                            return True
                    else:
                        return True
            except (KeyError, IndexError, ValueError) as e:
                # Handle specific exceptions here or raise a custom exceptions
                print(f"Error in check_maintain_conditions: {e}")
                return False
        return False

    def check_start_conditions(self):
        try:
            start_date = self.conditions.get("start").get('date', None)
            if start_date:
                return datetime.strptime(start_date, self.DATA_FORMAT) < datetime.now()
            return True
        except (KeyError, ValueError) as e:
            # Handle specific exceptions here or raise a custom exceptions
            print(f"Error in check_start_conditions: {e}")
            return False

    def check_expiry_conditions(self):
        try:
            expiry_date = self.conditions.get("expiry").get('date', None)
            if expiry_date:
                return datetime.strptime(expiry_date, self.DATA_FORMAT) > datetime.now()
            return True
        except (KeyError, ValueError) as e:
            # Handle specific exceptions here or raise a custom exceptions
            print(f"Error in check_expiry_conditions: {e}")
            return False

    def check_constraint_conditions(self):
        try:
            constraint_or = self.conditions.get("constraint_or")
            for transaction in self.transactions:
                index = -1
                for constraint in constraint_or:
                    balance = transaction.get("balances")
                    current_balance = balance.get("current")
                    if current_balance >= constraint.get("amount_greater"):
                        self.amount_to_check = constraint.get("amount_greater")
                        index += 1
                    else:
                        break
                if index != -1:
                    return index
        except (KeyError, IndexError) as e:
            # handle specific exceptions here or raise a custom exceptions
            print(f"Error in check_constraint_conditions: {e}")
            # You can choose to raise the exception or return a default value, depending on your use case
            raise e  # Raise the exception to be handled at a higher level
        return -1

    def get_bonus(self, index):
        return self.conditions.get("bonuses")[index]


# Sort and filter different transactions based on user account
class FormatAccountData:
    def __init__(self, data):
        # moved sorting of transaction data to the constructor to improve efficiency.
        self.transaction_data = self.sort_transaction_by_date(data)
        self.DATE_VALUE = "%Y-%m-%dT%H:%M:%SZ"

    def get_all_accounts_type(self, key):
        # modified get_all_accounts_type method to directly return the filtered data
        # instead of storing it in self.transaction_data.
        return list(filter(lambda d: d.get('official_name') == key, self.transaction_data))
        # self.transaction_data = list(filter(lambda d: d.get('official_name') == key, data) , self, data

    def get_unique_accounts(self):
        unique_accounts = set()
        for account in self.transaction_data:
            unique_accounts.add(account.get('account_id'))
        return list(unique_accounts)

    def sort_transaction_by_date(self, data):
        # simplified using a sorted method, returned immediately
        return sorted(data, key = lambda x: datetime.strptime(x['updated_at'], self.DATE_VALUE))
        # data.sort(key=lambda x: datetime.strptime(
        #     x['updated_at'], self.DATE_VALUE))
        # return data

    def get_all_account_data(self, account):
        return list(filter(lambda d: d.get('account_id') == account, self.transaction_data))


# Fetch all data from DynamoDB
def fetch_transactions_data():
    # response = table.scan()
    # data = response['Items']
    # return data
    # added a default return value of an empty list in case response["items"] is not present
    response = table.scan()
    return response.get("Items")


# Main function to call to identify accounts
def bonus_checker():
    try:
        all_transactions_data = fetch_transactions_data()

        # Loop for bank
        # for bank in CHECKER_DATA.keys():
        for bank, bank_conditions in banks.items(): # makes us able to directly iterate over key-value pairs
            # bank_conditions = CHECKER_DATA.get(bank)

            # Loop for bank conditions based on different account types
            for bank_condition in bank_conditions:
                # print("Running for account type: ", bank_condition.get("account_type").get("names")[0])
                account_type = bank_condition.get('account_type').get('names')[0]
                print("running for account type: ", account_type)


                format_data = FormatAccountData(all_transactions_data)
                # format_data.get_all_accounts_type(all_transactions_data, bank_condition.get("account_type").get("names")[0])
                format_data.get_all_accounts_type(all_transactions_data, account_type)
                unique_accounts = format_data.get_unique_accounts()
                print("All unique accounts; ", unique_accounts)

                # Loop on accounts
                for account in unique_accounts:
                    account_data = format_data.get_all_account_data(account)
                    sorted_account_data = format_data.sort_transaction_by_date(account_data)

                    # User Bank account transactions matched with bank conditions
                    bank_check = UserBankAccountCheck(sorted_account_data, bank_condition.get("conditions")[0])
                    start_condition = bank_check.check_start_conditions()
                    expiry_condition = bank_check.check_expiry_conditions()
                    constraint_condition_index = bank_check.check_constraint_conditions()
                    maintain_condition = bank_check.check_maintain_conditions()

                    # Condition checker for all the functions
                    # if start_condition and expiry_condition and maintain_condition and constraint_condition_index != -1:
                        # print(account, "won bonus", bank_check.get_bonus(constraint_condition_index).get("amount"))
                    if all([start_condition, expiry_condition, maintain_condition, constraint_condition_index != -1]):
                        bank_amount = bank_check.get_bonus(constraint_condition_index).get('amount')
                        print(account, 'won bonus', bank_amount)

    except botocore.exceptions.ClientError:
        raise
