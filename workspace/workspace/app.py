import datetime
import json
import logging
import os
import time

import polars as pl
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from openai import AzureOpenAI

from app_products import columns_blueprint, product_blueprint
from functions import generate_new_id, hash_password
from gpt import feedback_report, pickup_good_report, report_evaluation

app = Flask(__name__)
CORS(app)

# TeamC
api_base = "XXX"
api_version = "XXX"
api_key = "XXX"

deployment_name = "gpt-4o-mini"
model_name = "gpt-4o-mini"

client = AzureOpenAI(api_key=api_key, api_version="XXX", azure_endpoint=api_base)


class CodeGenResult(BaseModel):
    reply: str = Field(description="botの返信")
    flag: str = Field(description="不適切な言葉が含まれているかどうか")


parser = JsonOutputParser(pydantic_object=CodeGenResult)

prompt_template = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "あなたは営業職のアシスタントチャットボットです。\n出力形式は.txtで書かれます。\n{format_instructions}\n"
        ),
        HumanMessagePromptTemplate.from_template("{query}"),
    ],
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Register blueprints
app.register_blueprint(product_blueprint, url_prefix="/api/products")
app.register_blueprint(columns_blueprint, url_prefix="/api/columns")

# Load CSV data
users_table = pl.read_csv("../data/csv/Users.csv", encoding="utf8")
products_table = pl.read_csv("../data/csv/Products.csv", encoding="utf8")
large_category_table = pl.read_csv("../data/csv/Large_category.csv", encoding="utf8")
small_category_table = pl.read_csv("../data/csv/Small_category.csv", encoding="utf8")
reports_table = pl.read_csv("../data/csv/Reports.csv", encoding="utf8")
report_tags_table = pl.read_csv("../data/csv/Report_tags.csv", encoding="utf8")
posts_table = pl.read_csv("../data/csv/Posts.csv", encoding="utf8")
post_tags_table = pl.read_csv("../data/csv/Post_tags.csv", encoding="utf8")
tag_table = pl.read_csv("../data/csv/Tag.csv", encoding="utf8")
columns_table = pl.read_csv("../data/csv/Columns.csv", encoding="utf8")
sales_table = pl.read_csv("../data/csv/Sales.csv", encoding="utf8")
sales_detail_table = pl.read_csv("../data/csv/Sales_detail.csv", encoding="utf8")


# 全商品の取得
@app.route("/api/all_products", methods=["GET"])
def get_all_products():
    products_hierarchy = {}
    # 全ての大カテゴリを取得
    large_categories = large_category_table.to_dicts()
    # 全ての小カテゴリを取得
    small_categories = small_category_table.to_dicts()
    # 全ての商品データを取得
    products = products_table.to_dicts()
    # 大カテゴリごとに整理
    for large_category in large_categories:
        large_category_name = large_category["large_category_name"]
        large_category_id = large_category["large_category_id"]

        products_hierarchy[large_category_name] = {}

        # 該当する小カテゴリを取得
        for small_category in small_categories:
            if small_category["large_category_id"] == large_category_id:
                small_category_name = small_category["small_category_name"]

                # 該当する商品の名前をリストに追加
                products_hierarchy[large_category_name][small_category_name] = [
                    {
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                    }
                    for product in products
                    if product["small_category"] == small_category_name
                ]

    return products_hierarchy


# ログイン機能
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("userid")
    password = data.get("password")
    hashed_password = hash_password(password)

    # メールアドレスがユーザーテーブルに存在するかを確認
    if user_id in users_table["email"].to_list():
        # 保存されているパスワードと比較
        stored_password = users_table.filter(users_table["email"] == user_id)[
            "password"
        ].item(0)
        if hashed_password == stored_password:
            # ユーザIDを取得して返す
            user_id_value = users_table.filter(users_table["email"] == user_id)[
                "user_id"
            ].item(0)
            return jsonify({"success": True, "user_id": user_id_value})

    # エラーレスポンスを返す
    return (
        jsonify(
            {"success": False, "message": "ユーザ名かパスワードが間違っています。"}
        ),
        401,
    )


# ユーザ読み込み機能
@app.route("/api/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    # ユーザーIDでユーザー情報を検索
    user_data = users_table.filter(pl.col("user_id") == user_id)
    if user_data.height == 0:
        return jsonify({"error": "User not found"}), 404

    # 必要な情報だけを選択し、最初のレコードのみを取得
    user_info = user_data.select(
        ["user_id", "name", "email", "occupation", "profile", "calender_id"]
    ).to_dicts()[0]

    return jsonify(user_info)


# プロフィールのレビュー投稿取得用
@app.route("/api/profile_post/<user_id>", methods=["GET"])
def profile_post(user_id):
    tags = request.args.get("tags")
    if tags:
        tags = tags.split(",")  # タグをカンマで分割してリストに変換

    products_table = pl.read_csv("../data/csv/Products.csv", encoding="utf8")
    posts_table = pl.read_csv(
        "../data/csv/Posts.csv", encoding="utf8", dtypes={"user_id": pl.Utf8}
    )
    post_tags_table = pl.read_csv("../data/csv/Post_tags.csv", encoding="utf8")
    tag_table = pl.read_csv("../data/csv/Tag.csv", encoding="utf8")

    small_category_table = pl.read_csv("../data/csv/Small_category.csv", encoding="utf8")
    large_category_table = pl.read_csv("../data/csv/Large_category.csv", encoding="utf8")

    post_tags = post_tags_table.join(tag_table, on="tag_id")
    posts_table = posts_table.join(products_table, on="product_id")

    posts_table = posts_table.join(small_category_table, left_on = "small_category", right_on = "small_category_name")
    posts_table = posts_table.join(large_category_table, on="large_category_id")

    if tags:
        filtered_post_ids = (
            post_tags.filter(pl.col("tag").is_in(tags))["post_id"].unique().to_list()
        )
        profile_post = posts_table.filter(
            (pl.col("user_id") == user_id)
            & (pl.col("post_id").is_in(filtered_post_ids))
        ).to_dicts()
    else:
        profile_post = posts_table.filter(pl.col("user_id") == user_id).to_dicts()

    for post in profile_post:
        post["tags"] = post_tags.filter(pl.col("post_id") == post["post_id"])[
            "tag_name"
        ].to_list()
    print(profile_post[0])

    return jsonify(profile_post)


# 商品個別ページのレビュー投稿取得用
@app.route("/api/product_post/<product_id>", methods=["GET"])
def product_post(product_id):
    tags = request.args.get("tags")
    tags = None
    if tags:
        tags = tags.split(",")

    # CSVファイルを読み込む
    posts_table = pl.read_csv("../data/csv/Posts.csv", encoding="utf8")
    users_table = pl.read_csv("../data/csv/Users.csv", encoding="utf8")
    post_tags_table = pl.read_csv("../data/csv/Post_tags.csv", encoding="utf8")
    tag_table = pl.read_csv("../data/csv/Tag.csv", encoding="utf8")

    # Post_tagsとTagテーブルを結合してタグ情報を取得
    post_tags = post_tags_table.join(tag_table, on="tag_id")

    # 投稿データとユーザプロフィールを結合
    posts_data = posts_table.join(users_table.select(["user_id", "name"]), on="user_id")

    # 親投稿と子投稿を分ける
    parent_post_table = posts_data.filter(pl.col("parent_id") == "NULL").filter(
        pl.col("product_id") == product_id
    )
    child_post_table = posts_data.filter(pl.col("parent_id") != "NULL").filter(
        pl.col("product_id") == product_id
    )

    if tags:
        filtered_post_ids = (
            post_tags.filter(pl.col("tag").is_in(tags))["post_id"].unique().to_list()
        )
        parent_posts = parent_post_table.filter(
            (pl.col("product_id") == product_id)
            & (pl.col("post_id").is_in(filtered_post_ids))
        ).to_dicts()
    else:
        parent_posts = parent_post_table.filter(
            pl.col("product_id") == product_id
        ).to_dicts()

    # 親投稿に対応する子投稿をネストして追加
    for parent_post in parent_posts:
        child_posts = child_post_table.filter(
            pl.col("parent_id") == parent_post["post_id"]
        ).to_dicts()
        for child_post in child_posts:
            child_post["tags"] = post_tags.filter(
                pl.col("post_id") == child_post["post_id"]
            )["tag_name"].to_list()
        parent_post["children"] = child_posts
        parent_post["tags"] = post_tags.filter(
            pl.col("post_id") == parent_post["post_id"]
        )["tag_name"].to_list()

    return jsonify(parent_posts)


# プロフィールの日報取得用
@app.route("/api/reports_with_tags/<user_id>", methods=["GET"])
def reports_with_tags(user_id):
    # クエリパラメータからタグ名のリストを取得（例: /api/reports_with_tags/123?tags=tag1,tag2）
    tags = request.args.get("tags")
    if tags:
        tags = tags.split(",")  # タグをカンマで分割してリストに変換

    # CSVファイルの読み込み
    reports_table = pl.read_csv(
        "../data/csv/Reports.csv", encoding="utf8", dtypes={"user_id": pl.Utf8}
    )
    report_tags_table = pl.read_csv("../data/csv/Report_tags.csv", encoding="utf8")
    tag_table = pl.read_csv("../data/csv/Tag.csv", encoding="utf8")

    # report_tagsテーブルとtagテーブルを結合
    report_tags = report_tags_table.join(tag_table, on="tag_id")

    # タグでフィルタリング
    if tags:
        filtered_report_ids = (
            report_tags.filter(pl.col("tag").is_in(tags))["report_id"]
            .unique()
            .to_list()
        )
        filtered_reports = reports_table.filter(
            (pl.col("user_id") == user_id)
            & (pl.col("report_id").is_in(filtered_report_ids))
        ).to_dicts()
    else:
        filtered_reports = reports_table.filter(pl.col("user_id") == user_id).to_dicts()

    # 各日報に関連するタグを取得
    for report in filtered_reports:
        report["tags"] = report_tags.filter(pl.col("report_id") == report["report_id"])[
            "tag_name"
        ].to_list()
        report["material"] = report["material"].replace("_", "\n")

    return jsonify(filtered_reports)


# invoice作成用
@app.route("/api/invoice/<product_id>", methods=["GET"])
def get_product(product_id):
    print(product_id)
    product = products_table.filter(pl.col("product_id") == product_id)
    if product.is_empty():
        return jsonify({"error": "Product not found"}), 404

    product_info = product.select(
        [pl.col("product_id"), pl.col("product_name"), pl.col("price")]
    ).to_dicts()[0]

    return jsonify(product_info)


@app.route("/api/save_sales", methods=["POST"])
def save_sales():
    """
    データ形式
    {'user_id': '93852109', 'sales_detail': [{'product_id': '1PF787HVD9', 'quantity': 1}], 'total_amount': 13900}
    """
    # Sales.csv をすべての列を Utf8 型として読み込む
    sales_table = pl.read_csv(
        "../data/csv/Sales.csv",
        encoding="utf8",
        dtypes={col: pl.Utf8 for col in pl.scan_csv("../data/csv/Sales.csv").columns},
    )

    # Sales_detail.csv をすべての列を Utf8 型として読み込む
    sales_detail_table = pl.read_csv(
        "../data/csv/Sales_detail.csv",
        encoding="utf8",
        dtypes={
            col: pl.Utf8 for col in pl.scan_csv("../data/csv/Sales_detail.csv").columns
        },
    )

    all_sales_id = sales_table["sales_id"].to_list()
    all_sales_detail_id = sales_detail_table["sales_detail_id"].to_list()

    data = request.json

    user_id = data.get("user_id")
    sales_detail = data.get("sales_detail")
    total_sales = data.get("total_amount")
    # 売り上げた商品種類数
    total_count = len(sales_detail)

    sale_id = generate_new_id(id_list=all_sales_id, count=1, length=14)[0]
    sale_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Salesテーブルに保存
    new_sale = {
        "sales_id": [sale_id],
        "user_id": [user_id],
        "total_sales": [str(total_sales)],
        "sale_date": [sale_date],
        "created_at": [created_at],
        "deleted_at": ["NULL"],
    }
    sales_table = sales_table.vstack(pl.DataFrame(new_sale))
    sales_table.write_csv("../data/csv/Sales.csv")

    all_sales_detail_id = generate_new_id(
        id_list=all_sales_detail_id, count=total_count, length=16
    )
    all_sales_parent_id = [sale_id for _ in range(total_count)]
    all_product_id = []
    all_quantity = []
    for product in sales_detail:
        all_product_id.append(product["product_id"])
        all_quantity.append(str(product["quantity"]))  # 文字列にキャスト

    new_sale_detail = {
        "sales_detail_id": all_sales_detail_id,
        "sales_id": all_sales_parent_id,
        "product_id": all_product_id,
        "quantity": all_quantity,
    }
    sales_detail_table = sales_detail_table.vstack(pl.DataFrame(new_sale_detail))

    sales_detail_table.write_csv("../data/csv/Sales_detail.csv")

    return jsonify({"message": "Sales data saved successfully"})


# 日報のフィードバック取得
@app.route("/api/report_feedback", methods=["POST"])
def get_feedback():

    data = request.json  # リクエストからJSONデータを取得
    this_report = data.get("this_report")  # this_reportを取得
    reports_table = pl.read_csv(
        "../data/csv/Reports.csv",
        encoding="utf8",
        schema_overrides={"user_id": pl.Utf8},
    )
    report_score_table = pl.read_csv("../data/csv/Report_score.csv", encoding="utf8")
    top_reports = reports_table.join(report_score_table, on="report_id").filter(
        pl.col("score") == 10
    )

    top_report_id = set(top_reports["report_id"].to_list())
    top_report_dict = top_reports["report_id", "material", "score"].to_dicts()[:10]

    picked_id = pickup_good_report(top_report_dict, this_report, top_report_id)

    # お手本レポートの抽出(長さは3)
    picked_report = top_reports.filter(pl.col("report_id").is_in(picked_id))[
        "material"
    ].to_list()
    # 変更内容を反映させるように修正
    for i in range(len(picked_report)):
        picked_report[i] = picked_report[i].replace("_", "<br>")

    (score, feedback) = feedback_report(this_report)

    all_feedback = {
        "score": score,
        "feedback": feedback,
        "picked_report": picked_report,
    }
    return jsonify(all_feedback)


# 日報投稿
@app.route("/api/post_report", methods=["POST"])
def post_report():

    data = request.json

    # Reportsテーブル投稿
    reports_table = pl.read_csv(
        "../data/csv/Reports.csv", encoding="utf8", dtypes={"user_id": pl.Utf8}
    )
    report_tags_table = pl.read_csv(
        "../data/csv/Report_tags.csv", encoding="utf8", dtypes={"tag_id": pl.Utf8}
    )
    report_score_table = pl.read_csv(
        "../data/csv/Report_score.csv", encoding="utf8", dtypes={"score": pl.Utf8}
    )

    all_report_id = reports_table["report_id"].to_list()
    new_report_id = generate_new_id(id_list=all_report_id, count=1, length=10)[0]
    user_id = data.get("user_id")
    material = data.get("report")
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_report = {
        "report_id": new_report_id,
        "user_id": user_id,
        "material": material,
        "created_at": created_at,
        "updated_at": "NULL",
        "deleted_at": "NULL",
    }
    reports_table = reports_table.vstack(pl.DataFrame(new_report))

    reports_table.write_csv("../data/csv/Reports.csv")

    # Reports_tagsテーブル投稿
    (tags, scores) = report_evaluation(material)
    
    # タグを整数型に変換する
    new_tag_record = {
        "report_id": [new_report_id for _ in range(len(tags))],
        "tag_id": [int(tag) for tag in tags],  # 修正：tag_idをInt型に変換
    }
    report_tags_table = report_tags_table.vstack(pl.DataFrame(new_tag_record))

    # Report_scoreテーブル投稿
    new_score_record = {"report_id": new_report_id, "score": sum(scores)/len(scores)}  # 平均スコアを算出し、Float型に設定
    report_score_table = report_score_table.vstack(pl.DataFrame(new_score_record))

    report_tags_table.write_csv("../data/csv/Report_tags.csv")
    report_score_table.write_csv("../data/csv/Report_score.csv")

    return jsonify({"message": "Sales data saved successfully"})


@app.route("/api/chatbot", methods=["POST"])
def chatbot():

    user_message = request.json.get("message")

    prompt = prompt_template.format_prompt(query=user_message)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは高度な営業支援および商品検索アシスタントを行うAIです。営業支援と商品検索支援の2つの主要な機能を持ちます：\n\n"
                    "【営業支援】\n"
                    "• 効果的な営業戦略の立案と実行のアドバイス\n"
                    "• 顧客対応の改善と効果的なコミュニケーション技術の提案\n"
                    "• 反論処理と交渉スキルの向上支援\n"
                    "• 契約締結プロセスの最適化と成功率向上のための指導\n"
                    "• 営業パフォーマンス分析と改善点の特定\n\n"
                    "【商品検索支援】\n"
                    "以下のカテゴリに基づいて、ユーザーの要望に最適な商品を提案します。各商品についての詳細情報、特徴、利点も提供します。\n\n"
                    "【大カテゴリ】\n"
                    "1. モバイル  2. インターネット  3. セキュリティ  4. 複合機\n"
                    "5. サーバー  6. パソコン  7. IoT  8. 情報系システム  9. LED\n\n"
                    "【小カテゴリ】\n"
                    "1. スマートフォン (モバイル)\n"
                    "2. タブレット (モバイル)\n"
                    "3. ウェアラブルデバイス (モバイル)\n"
                    "4. モバイルアクセサリー (モバイル)\n"
                    "5. SIMカード (モバイル)\n"
                    "6. ブロードバンド (インターネット)\n"
                    "7. Wi-Fiサービス (インターネット)\n"
                    "8. クラウドストレージ (インターネット)\n"
                    "9. VPNサービス (インターネット)\n"
                    "10. Webホスティング (インターネット)\n"
                    "11. アンチウイルス (セキュリティ)\n"
                    "12. ファイアウォール (セキュリティ)\n"
                    "13. セキュリティカメラ (セキュリティ)\n"
                    "14. マルウェア対策 (セキュリティ)\n"
                    "15. オフィス用複合機 (複合機)\n"
                    "16. プリンター (複合機)\n"
                    "17. スキャナー (複合機)\n"
                    "18. ファクシミリ (複合機)\n"
                    "19. ファイルサーバー (サーバー)\n"
                    "20. メールサーバー (サーバー)\n"
                    "21. データベースサーバー (サーバー)\n"
                    "22. ウェブサーバー (サーバー)\n"
                    "23. デスクトップPC (パソコン)\n"
                    "24. ノートPC (パソコン)\n"
                    "25. ゲーミングPC (パソコン)\n"
                    "26. ビジネスPC (パソコン)\n"
                    "27. スマートホームデバイス (IoT)\n"
                    "28. スマートウォッチ (IoT)\n"
                    "29. スマートスピーカー (IoT)\n"
                    "30. IoTセンサー (IoT)\n"
                    "31. ERPシステム (情報系システム)\n"
                    "32. CRMシステム (情報系システム)\n"
                    "33. データ分析システム (情報系システム)\n"
                    "34. ビジネスインテリジェンス (情報系システム)\n"
                    "35. LED照明 (LED)\n"
                    "36. LEDディスプレイ (LED)\n"
                    "37. LED電球 (LED)\n\n"
                    "回答の際は、以下の点に注意してください：\n"
                    "1. ユーザーの質問や要望を正確に理解し、適切なカテゴリの商品を提案する\n"
                    "2. 商品の特徴や利点を簡潔かつ分かりやすく説明する\n"
                    "3. 営業支援に関しては、具体的で実践的なアドバイスを提供する\n"
                    "4. 必要に応じて、追加情報や詳細説明を提案する\n"
                    "5. 常に丁寧で専門的な言葉遣いを心がける\n\n"
                    "Userの投稿に対して、営業支援または商品検索支援を行ってください。ただし、箇条書きにはせず、普通の文章で答えてください。\n"
                ),
            },
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.9,
    )
    response_content = response.choices[0].message.content

    result = parser.parse(response_content)
    print("===== Jsonパーサー適用後の回答")
    print(result)
    print("===== カテゴリー")
    print(result.get("reply"))
    print("===== 感情")
    print(result.get("flag"))

    return jsonify({"reply": result.get("reply")})


@app.route("/api/product_recommend", methods=["POST"])
def product_recommend():
    data = request.json
    product_ids = data.get("products_ids")
    # ProductsテーブルとSales_detailテーブルの読み込み
    products_table = pl.read_csv(
        "../data/csv/Products.csv", encoding="utf8", dtypes={"small_category": pl.Utf8}
    )
    small_category = pl.read_csv(
        "../data/csv/Small_category.csv",
        encoding="utf8",
        dtypes={"small_category": pl.Utf8, "large_category": pl.Utf8},
    )
    large_category = pl.read_csv(
        "../data/csv/Large_category.csv",
        encoding="utf8",
        dtypes={"large_category": pl.Utf8},
    )
    products_data = products_table.join(
        small_category, left_on="small_category", right_on="small_category_name"
    )
    products_data = products_data.join(large_category, on="large_category_id")[
        "product_id", "product_name", "small_category", "large_category_name"
    ]

    sales_detail = pl.read_csv(
        "../data/csv/Sales_detail.csv",
        encoding="utf8",
        dtypes={"invoice_id": pl.Utf8, "product_id": pl.Utf8, "count": pl.Int32},
    )
    # 指定された商品が購入されているレコードをフィルタリングして invoice_id を取得
    sales_id_list = (
        sales_detail.filter(pl.col("product_id").is_in(product_ids))
        .select("sales_id")
        .unique()
    )
    # 指定された商品が購入されているもののみをフィルタリング
    sales_table = sales_detail.filter(
        pl.col("sales_id").is_in(sales_id_list["sales_id"])
    )
    aggregated_df = sales_table.group_by("product_id").agg(
        total_quantity=pl.sum("quantity")
    )
    # product_idsに含まれるものを除外
    filtered_df = aggregated_df.filter(~pl.col("product_id").is_in(product_ids))
    # quantityの上位2つを取得
    top_id_list = (
        filtered_df.sort("total_quantity", descending=True)
        .head(2)["product_id"]
        .to_list()
    )
    top_product_dicts = products_data.filter(
        pl.col("product_id").is_in(top_id_list)
    ).to_dicts()
    print(top_product_dicts)
    return jsonify({"top_product": top_product_dicts})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
