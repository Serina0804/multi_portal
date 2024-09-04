erDiagram

%% 商品機能
Products {
    string product_id PK "商品id"
    string product_name "商品名"
    string small_category FK "商品小カテゴリ"
    string description "仕様書"
    float price "価格"
    datetime created_at "作成日時"
    datetime updated_at "更新日時"
    datetime deleted_at "削除日時"
}

Large_category_name {
    string large_category_id PK "商品大カテゴリ"
    string large_category_name "商品大カテゴリ名"
}

Small_category_name {
    string small_category_id PK "商品小カテゴリ"
    string small_category_name "商品小カテゴリ名"
    string large_category_id FK "商品大カテゴリ"
}

%% ユーザ機能
Users {
    string user_id PK "主キー"
    string name "名前"
    string email "メールアドレス"
    string occupation "職種"
    string profile "経歴"
    string password "パスワード"
    string calender_id "カレンダーID"
    datetime created_at "作成日時"
    datetime updated_at "更新日時"
    datetime deleted_at "削除日時"
}

Reports {
    string report_id PK "主キー"
    string user_id FK "投稿ユーザ"
    string material "投稿内容"
    datetime created_at "作成日時"
    datetime updated_at "更新日時"
    datetime deleted_at "削除日時"
}

Report_tags {
    string report_id PK "主キー"
    string tag_id FK "タグID"
}

Report_score {
    string report_id PK "主キー"
    int score "点数"
}

%% レビュー機能
Posts {
    string post_id PK "主キー"
    string product_id FK "商品コード"
    string parent_id FK "親投稿コード"
    string user_id FK "投稿ユーザ"
    string material "投稿内容"
    int likes_count "いいね数"
    datetime created_at "作成日時"
    datetime updated_at "更新日時"
    datetime deleted_at "削除日時"
}

Post_tags {
    string post_id FK "投稿データID"
    string tag_id FK "タグID"
}

%% その他
Tag {
    string tag_id PK "主キー"
    string tag "タグ名"
}

Columns {
    string column_id PK "記事ID"
    string user_id FK "ユーザID"
    string material "記事内容"
    datetime created_at "作成日時"
    datetime updated_at "更新日時"
    datetime deleted_at "削除日時"
}

Sales {
    string invoice_id PK "請求ID"
    string user_id FK "ユーザID"
    datetime created_at "作成日時"
    datetime deleted_at "削除日時"
}

Sales_detail {
    string invoice_id FK "請求ID"
    string product_id FK "商品ID"
    int count "購入数"
    datetime created_at "作成日時"
    datetime deleted_at "削除日時"
}

%% リレーション
Products ||--o{ Small_category_name : "belongs to"
Small_category_name }o--|| Large_category_name : "belongs to"

Users ||--o{ Reports : "creates"
Reports ||--o{ Report_tags : "has"
Reports ||--o{ Report_score : "has"

Users ||--o{ Posts : "creates"
Posts ||--o{ Post_tags : "has"

Tag ||--o{ Post_tags : "used in"
Tag ||--o{ Report_tags : "used in"

Users ||--o{ Columns : "writes"
Users ||--o{ Sales : "makes"
Sales ||--o{ Sales_detail : "contains"
Products ||--o{ Sales_detail : "sold in"
