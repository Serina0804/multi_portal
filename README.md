# SNSライクなマルチポータルサイト

## 目的

営業部の業務改善のためのDXシステム

## システム作成にあたっての課題
- 時間不足
    - オフィスまるごとに関する商品数が多く、理解が追いつかない
    - 書類や日報作成に時間を囚われてしまっている
- 情報の属人化
    - 商談に必要な情報を収集する時間が足りない
    - 必要な情報を誰に聞けばいいかがわからない
    - 日報を上手に書きたいが、いまいち書き方がよくわかっていない

## プロダクトの目標設定

**誰もが短時間で、効率的で、高品質な情報収集や作業を実現**する**マルチポータルサイト**

機能
- 縦割りの排除と情報シェアの促進
- 商品のレコメンド
- 日報作成のサポート

## 使用技術

| Category  | Technology Stack |
| ------------- | ------------- |
| Frontend  | HTML, CSS, TypeScript, React  |
| Backend  | Python, Flask, Langchain  |
| Database  | CSV(polars)  |

## ER図

<img width="389" alt="スクリーンショット 2024-09-04 16 40 08" src="https://github.com/user-attachments/assets/1cba031d-4c8e-47cf-8df4-09f1c68f1359">

- 合計**12**テーブルを作成
- 全テーブルで第三正規化を目指す
    - 効率なデータ管理を実現し、システム統合やアップデートにも容易に対応
- 商品投稿や日報に対してタグをつけることによって、データを柔軟に検索可能
    - 必要な情報への時短を実現

## 機能

### ページ遷移図
<img width="557" alt="スクリーンショット 2024-09-04 16 44 45" src="https://github.com/user-attachments/assets/51d328ad-cf68-47e7-bc4f-fcf88b22634a">

### 各ページ機能

#### ログインページ

<img width="128" alt="スクリーンショット 2024-09-04 16 46 52" src="https://github.com/user-attachments/assets/203053cf-af4e-4d1e-b31d-27a1bbb106ed">

- ログイン時のエラーメッセージでユーザIDかパスワードかを特定できないようにし、セキュリティを強化
- データベースにはパスワード原文でなく、ハッシュ化して保存


#### プロフィールページ

<img width="213" alt="スクリーンショット 2024-09-04 16 48 49" src="https://github.com/user-attachments/assets/abb416f7-d8d0-48a8-a279-a62798e60226">

機能：レビュー投稿、日報投稿のタグ生成
- LLM(GPT-4o-mini)によるタグ生成
    - 投稿内容からpostごとにpost_tagを割り当てる
    - post_idを取得し、postごとのpost_tagを呼び出すAPIを作成


#### 日報生成ページ

<img width="208" alt="スクリーンショット 2024-09-04 16 52 12" src="https://github.com/user-attachments/assets/be2aabc6-4010-46a7-b8fd-7bffa99d8c1c">

機能：日報作成のサポート（日報サンプルの選択、作成日報の評価・フィードバック）
- LLM(GPT-4o-mini)の使用
    - 日報サンプルの選択
        - 入力した内容に近く、評価の良い日報のサンプルを3つ表示
        - パラメータ　temperature == 1
            - 毎回なるべくランダムにサンプル日報を選択可能
    - 作成日報の評価・フィードバック
        - 作成した日報を内容・具体性・課題の3つの観点から５段階で評価、フィードバックを作成
        - パラメータ　temperature == 0
            - 毎回一貫した評価基準で評価可能

デモ動画：https://youtu.be/867n3mQATXk

#### 商品一覧ページ

<img width="164" alt="スクリーンショット 2024-09-04 16 58 31" src="https://github.com/user-attachments/assets/530191e9-66ec-4304-9926-1e994edd338b">

機能：商品一覧の表示、チャットボットによる商品レコメンドシステム
- 特定の商品の検索をサポート
    - Q.  〇〇の商品はどこのカテゴリー？
    - A.  「IoT」のカテゴリ

デモ動画：https://youtube.com/shorts/5pFW1trZkxU?feature=share



