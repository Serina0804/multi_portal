import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './header.css';

const Header: React.FC = () => {
  // セッションストレージからuserIdを取得
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const storedUserId = sessionStorage.getItem('userid');
    setUserId(storedUserId);
  }, []);

  return (
    <header className="header-container">
      <nav>
        <ul className="nav-list">
          <li className="nav-item">
            <Link to="/product" className="nav-link">商品一覧</Link>
          </li>
          <li className="nav-item">
            {userId ? (
              <Link to={`/profile/${userId}`} className="nav-link">マイプロフィール</Link>
            ) : (
              <Link to="/login" className="nav-link">ログイン</Link>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
