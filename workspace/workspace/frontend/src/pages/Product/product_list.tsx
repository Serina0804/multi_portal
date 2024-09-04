import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../Header/header'; // Header コンポーネントをインポート
import Accordion from './accordion'; // アコーディオンコンポーネントをインポート
import Chatbot from './chatbot'; // Chatbot コンポーネントをインポート
import './product_list.css'; // 商品リストのスタイル

// 商品の型を定義
type Product = {
  product_id: string;
  product_name: string;
};

// カテゴリーの型を定義
type Category = {
  [key: string]: {
    [subcategory: string]: Product[];
  };
};

const ProductList: React.FC = () => {
  const [categories, setCategories] = useState<Category>({});

  // APIから商品リストを取得するためのuseEffectフック
  useEffect(() => {
    (async () => {
      await fetch('http://127.0.0.1:3000/api/all_products') // Flaskサーバーのエンドポイントを指定
        .then(response => response.json())
        .then((data: Category) => {
          console.log(data);
          setCategories(data);
        })
        .catch(error => console.error('Error fetching products:', error));
    })();
  }, []);

  return (
    <div>
      <Header />
      <div className="product-list-container">
        <h2>商品リスト</h2>
        {Object.entries(categories).map(([categoryName, subcategories]) => (
          <Accordion
            key={categoryName}
            title={categoryName}
            content={
              Object.entries(subcategories).map(([subcategoryName, products]) => (
                <Accordion
                  key={subcategoryName}
                  title={subcategoryName}
                  content={
                    <ul className="product-list">
                      {products.map((product) => (
                        <li key={product.product_id} className="product-item">
                          <Link to={`/product/${product.product_id}`} className="product-link">
                            <span className="product-name">{product.product_name}</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  }
                />
              ))
            }
          />
        ))}
      </div>
      {/* チャットボットの追加 */}
      <Chatbot />
    </div>
  );
};

export default ProductList;
