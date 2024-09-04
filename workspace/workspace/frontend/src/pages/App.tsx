import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import Login from './Login/login.tsx';
import ProductDetail from './Product/product.tsx';
import Product_list from './Product/product_list.tsx';
import Profile from './Profile/profile.tsx';
import Invoice from './Product/invoice.tsx';
import Post_report from './Report/post_report.tsx';



function App() {
  return (
    <>
      <Router>
          <Routes>
            {/* 初期状態でLoginページにリダイレクト */}
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile/:userId" element={<Profile />} />
            <Route path="/product" element={<Product_list />} />
            <Route path="/product/:productId" element={<ProductDetail />} />
            <Route path="/invoice" element={<Invoice />} />
            <Route path="/report" element={<Post_report />} />
          </Routes>
      </Router>
    </>
  );
}

export default App;
