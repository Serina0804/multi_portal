import React, { useState, useEffect } from 'react';
import jsPDF from 'jspdf';
import './invoice.css';
import NotoSansJP from '../../fonts/NotoSansJP-Regular.ttf';
import Header from '../Header/header';

interface CartItem {
  id: number;
  name: string; // 商品名を追加
  count: number;
  price: number; // 各商品の単価を保持する
}

const InvoicePage: React.FC = () => {
  // セッションストレージからuserIdを取得
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const storedUserId = sessionStorage.getItem('userid');
    setUserId(storedUserId);
  }, []);

  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [totalAmount, setTotalAmount] = useState<number>(0);

  useEffect(() => {
    const savedCartItems = sessionStorage.getItem('cartItems');
    if (savedCartItems) {
      const parsedCartItems = JSON.parse(savedCartItems).map((item: any) => ({
        ...item,
        name: '', // 初期値を設定
        price: 0, // 初期値を設定
      }));

      Promise.all(parsedCartItems.map(async (item: any) => {
        const response = await fetch(`http://127.0.0.1:3000/api/invoice/${item.id}`);
        const productData = await response.json();
        return {
          ...item,
          name: productData.product_name, // APIから取得した商品名を設定
          price: productData.price, // APIから取得した価格を設定
        };
      })).then((items) => {
        setCartItems(items);
        const total = items.reduce((sum: number, item: CartItem) => sum + item.count * item.price, 0);
        setTotalAmount(total);
      });
    }
  }, []);

  const saveSalesToDatabase = async () => {
    const salesDetail = cartItems.map(item => ({
      product_id: item.id,
      quantity: item.count,
    }));

    const response = await fetch('http://127.0.0.1:3000/api/save_sales', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,  // ユーザーIDは実際のログインユーザーから取得
        sales_detail: salesDetail,
        total_amount: totalAmount,
      }),
    });

    if (response.ok) {
      console.log('Sales data saved successfully');
    } else {
      console.error('Failed to save sales data');
    }
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    
    // 日本語フォントの追加
    doc.addFont(NotoSansJP, 'NotoSansJP', 'normal');
    doc.setFont('NotoSansJP');
    
    doc.setFontSize(18);
    doc.text("納品書", 105, 15, { align: "center" });
    
    doc.setFontSize(12);
    doc.text(`合計金額: ${totalAmount} 円`, 14, 25);

    const startX = 14;
    const startY = 40;
    const rowHeight = 10;

    doc.text("商品ID", startX, startY);
    doc.text("数量", startX + 60, startY);
    doc.text("単価", startX + 100, startY);
    doc.text("小計", startX + 140, startY);

    cartItems.forEach((item, index) => {
      const yPos = startY + rowHeight * (index + 1);
      doc.text(`${item.id}`, startX, yPos);
      doc.text(`${item.count}`, startX + 60, yPos);
      doc.text(`${item.price}`, startX + 100, yPos);
      doc.text(`${item.count * item.price}`, startX + 140, yPos);
    });

    doc.save("納品書.pdf");


    // 決済情報を保存
    saveSalesToDatabase();

    // セッションストレージからカート情報を削除し、状態をリセット
    sessionStorage.removeItem('cartItems');
    setCartItems([]);
    setTotalAmount(0);
  };

  return (
    <div>
      <Header />
      <div className="invoice-container">
        <h1>納品書の概算</h1>
        <table className="invoice-table">
          <thead>
            <tr>
              <th>商品ID</th>
              <th>商品名</th>
              <th>数量</th>
              <th>金額 (円)</th>
              <th>総金額 (円)</th>
            </tr>
          </thead>
          <tbody>
            {cartItems.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.name}</td>
                <td>{item.count}</td>
                <td>{item.price}</td>
                <td>{item.count * item.price}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={4}><strong>総金額</strong></td>
              <td><strong>{totalAmount} 円</strong></td>
            </tr>
          </tfoot>
        </table>
        <button className="generate-pdf-button" onClick={generatePDF}>決済</button>
      </div>
    </div>
  )
}

export default InvoicePage;
