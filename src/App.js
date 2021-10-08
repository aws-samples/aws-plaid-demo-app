import { Auth } from 'aws-amplify';
import { withAuthenticator } from '@aws-amplify/ui-react';
import { Layout, PageHeader, Button } from 'antd';
import Plaid from './Plaid';
import './App.css';

const { Content, Footer } = Layout;

function App() {

  function handleSignout() {
    Auth.signOut()
      .then(() => window.location.reload())
      .catch(err => console.log(err));
  }

  return (
    <Layout className="layout">
      <PageHeader
        ghost={false}
        title="Plaid AWS Quickstart"
        extra={[
          <Button onClick={handleSignout}>Signout</Button>
        ]}
      />
      <Content style={{ padding: '0 50px' }}>
        <div className="site-layout-content">
          <Plaid />
        </div>
      </Content>
    </Layout>
  );
}

export default withAuthenticator(App);
