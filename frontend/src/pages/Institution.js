import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Divider, Flex, Heading, View, Tabs, TabItem, Button } from '@aws-amplify/ui-react';
import Accounts from '../components/Accounts';
import Transactions from '../components/Transactions';
import InvestmentAccounts from '../components/InvestmentAccounts';
import Holdings from '../components/Holdings';
import Disconnect from '../components/Disconnect';

export default function Institution() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [accountMap, setAccountMap] = useState({});
  const [investmentAccountMap, setInvestmentAccountMap] = useState({});
  const [institutionName, setInstitutionName] = useState('this institution');

  const updateAccounts = (accounts) => {
    const accountMap = accounts.reduce((acc, cur) => {
      acc[cur.account_id] = cur;
      return acc;
    }, {});
    setAccountMap(accountMap);
    
    // If any account has an institution_name property, use it
    if (accounts.length > 0 && accounts[0].institution_name) {
      setInstitutionName(accounts[0].institution_name);
    }
  };

  const updateInvestmentAccounts = (accounts) => {
    const accountMap = accounts.reduce((acc, cur) => {
      acc[cur.account_id] = cur;
      return acc;
    }, {});
    setInvestmentAccountMap(accountMap);
  };

  const navigateToInvestmentDashboard = () => {
    navigate(`/investment/${id}`);
  };

  return (
    <Flex direction="column">
      <Divider/>
      <Flex direction="row" justifyContent="space-between" alignItems="center">
        <Heading level={5}>Institution Dashboard</Heading>
        <Disconnect id={id} institutionName={institutionName} />
      </Flex>
      
      <Tabs justifyContent="center">
        <TabItem title="Banking">
          <Flex direction="row">
            <View width="50%">
              <Heading level={6}>Accounts</Heading>
              <Accounts id={id} updateAccounts={updateAccounts}/>
            </View>
            <View width="50%">
              <Heading level={6}>Transactions</Heading>
              <Transactions id={id} accounts={accountMap}/>
            </View>
          </Flex>
        </TabItem>
        <TabItem title="Investments">
          <Flex direction="column">
            <View>
              <Heading level={6}>Investment Accounts</Heading>
              <InvestmentAccounts id={id} updateAccounts={updateInvestmentAccounts}/>
            </View>
            <View marginTop="1rem">
              <Heading level={6}>Holdings</Heading>
              <Holdings id={id} accounts={investmentAccountMap}/>
            </View>
          </Flex>
        </TabItem>
      </Tabs>
    </Flex>
  );
}
