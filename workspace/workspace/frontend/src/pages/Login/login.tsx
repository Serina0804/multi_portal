import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './login.css';

const LoginPage: React.FC = () => {
  const [userid, setUserid] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const isValidUserid = (userid: string): boolean => {
    const regex = /^[a-zA-Z0-9._%+-]+@otsuka\.co\.jp$/;
    return regex.test(userid);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    if (!isValidUserid(userid)) {
      setError('ログインに失敗しました。UserIDの形式が正しくありません。');
      return;
    }

    setError('');

    try {
      const response = await fetch('http://localhost:3000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userid, password }),
      });

      const data = await response.json();

      if (response.ok && data.user_id) {
        // 成功時の処理
        sessionStorage.setItem('userid', data.user_id);
        navigate(`/profile/${data.user_id}`); // パスパラメータを使用する形式に更新
      } else {
        // 失敗時の処理
        setError('ログインに失敗しました。ユーザIDまたはパスワードが正しくありません。');
      }
    } catch (error) {
      console.error('ログイン処理中にエラーが発生しました:', error);
      setError('ログインに失敗しました。サーバーエラーです。');
    }
  };

  return (
    <div className="login-container">
      <h2>ログインページ</h2>
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="userid">UserID:</label>
          <input
            type="text"
            id="userid"
            value={userid}
            onChange={(e) => setUserid(e.target.value)}
            className="form-control"
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-control"
          />
        </div>
        <button type="submit" className="login-button">
          ログイン
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
