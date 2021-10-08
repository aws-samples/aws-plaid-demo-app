import { useState, useEffect } from 'react';
import { API, Auth } from 'aws-amplify';
import { Button, Typography, Spin, Table } from 'antd';
import { BankOutlined } from '@ant-design/icons';
import './plaid.css';
import PlaidLink from './PlaidLink';
import config from '../aws-exports';

const apiName = config.aws_cloud_logic_custom[0].name;

const { Title } = Typography;

const cols = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Amount',
    dataIndex: 'amount',
    key: 'amount',
  },
  {
    title: 'Date',
    dataIndex: 'date',
    key: 'date',
  },
  {
    title: 'Account ID',
    dataIndex: 'account_id',
    key: 'account_id',
  },
  {
    title: 'Payment Channel',
    dataIndex: 'payment_channel',
    key: 'payment_channel',
  },
  {
    title: 'Transaction Type',
    dataIndex: 'transaction_type',
    key: 'transaction_type',
  },
];

export default function Plaid() {
  const [connecting, setConnecting] = useState(false);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [trans, setTrans] = useState([]);

  const getTransactions = async () => {
    setLoading(true);
    const user = await Auth.currentAuthenticatedUser();
    console.log(user);
    try {
      const { sub } = user.attributes;
      const trans = await API.get(apiName, `/v1/transactions?sub=${sub}`);
      console.log('transsslkj', trans);
      setTrans(trans.msg);
      setUser(user);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      setUser(user);
      console.log('erorororor trans', err);
    }
  };

  useEffect(() => {
    getTransactions();
  }, []);

  const handleGetToken = async () => {
    setConnecting(true);
    try {
      const { sub } = user.attributes;
      const res = await API.get(apiName, `/v1/token?sub=${sub}`);
      setToken(res.token);
    } catch (err) {
      console.log('errr', err);
    }
  };

  const handleSuccess = async (token) => {
    try {
      const res = await API.post(apiName, '/v1/token', {
        body: {
          token,
          sub: user.attributes.sub,
        }
      });
      console.log('heres the response', res);
      getTransactions();
    } catch (err) {
      console.log('errror with post', err);
    }
  };

  if (loading) {
    return (
      <div className="plaid_container">
        <Spin />
      </div>
    );
  }

  if (trans.length) {
    return (
      <div className="plaid_container_table">
        <Title>Transactions</Title>
        <Table columns={cols} dataSource={trans} />
      </div>
    );
  }

  return (
    <div className="plaid_container">
      <Title>Connect your Bank Account</Title>
      <Button
        type="primary"
        size="large"
        className="plaid_btn"
        icon={<BankOutlined />}
        loading={connecting}
        // disabled={!ready}
        onClick={handleGetToken}
      >
        CONNECT WITH PLAID
      </Button>
      {token ? (
        <PlaidLink
          token={token}
          onSuccess={handleSuccess}
          onExit={() => setConnecting(false)}
        />
      ) : null}
    </div>
  );
}