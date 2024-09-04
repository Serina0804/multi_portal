# プロジェクト構成

このプロジェクトはReactを使用したウェブアプリケーションです。以下は、プロジェクトのディレクトリ構造と各ディレクトリ・ファイルの役割について説明します。

## ディレクトリ構造

```plaintext
src/
│
├── App.tsx
├── index.tsx
├── routes/
│   ├── AppRoutes.tsx
│   └── ProtectedRoute.tsx
└── pages/
    ├── Login/
    │   ├── Login.tsx
    │   └── Login.css
    ├── Product/
    │   ├── Product.tsx
    │   └── Product.css
    └── Profile/
        ├── Profile.tsx
        └── Profile.css
```

Login: ログインページ

商品リスト: 商品リストページ product_list
        kyogoku/Product
Product: 商品ページ
        koygoku/Product/product_id
Profile: プロフィールページ　
        kyogoku/Profile/user_id
