import { useParams } from 'react-router-dom';
import { useState } from 'react';
import { Divider, Flex, Heading, View, Tabs } from '@aws-amplify/ui-react';
import InvestmentAccounts from '../components/InvestmentAccounts';
import Holdings from '../components/Holdings';
import Disconnect from '../components/Disconnect';

export default function InvestmentDashboard() {
  const { id } = useParams();
  const [accountMap, setAccountMap] = useState({});
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

  return (
    <Flex direction="column">
      <Divider />
      <Flex direction="row" justifyContent="space-between" alignItems="center">
        <Heading level={5}>Investment Dashboard</Heading>
        <Disconnect id={id} institutionName={institutionName} />
      </Flex>
      
      <Tabs justifyContent="center"
        items={[
          {
            label: "Investment Accounts",
            content: (
              <View>
                <InvestmentAccounts id={id} updateAccounts={updateAccounts}/>
              </View>
            )
          },
          {
            label: "Holdings",
            content: (
              <View>
                <Holdings id={id} accounts={accountMap} />
              </View>
            )
          }
        ]}
      />
    </Flex>
  );
}