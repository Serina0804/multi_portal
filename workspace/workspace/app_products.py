import os
from pathlib import Path

import polars as pl
from dotenv import load_dotenv
from flask import Blueprint, jsonify, send_file

# Register blueprints

# プロジェクトのルートディレクトリを取得
project_root = Path(__file__).parents[1]
print(f"Project root: {project_root}")

# .envファイルの読み込み
env_path = project_root / ".env"
print(f"Looking for .env file at: {env_path}")
load_dotenv(env_path)


# 環境変数の取得とデバッグ出力
def get_env_var(var_name, default_value):
    value = os.getenv(var_name)
    if value is None:
        print(
            f"Warning: {var_name} not found in .env, using default value: {default_value}"
        )
        return default_value
    print(f"Loaded {var_name}: {value}")
    return value


product_csv_path = get_env_var("PRODUCT_CSV_PATH", "data/csv/Products.csv")
large_category_csv_path = get_env_var(
    "LARGE_CATEGORY_CSV_PATH", "data/csv/Large_category.csv"
)
small_category_csv_path = get_env_var(
    "SMALL_CATEGORY_CSV_PATH", "data/csv/Small_category.csv"
)
post_csv_path = get_env_var("POST_CSV_PATH", "data/csv/Posts.csv")
post_tag_csv_path = get_env_var("POST_TAG_CSV_PATH", "data/csv/Post_tags.csv")
columns_csv_path = get_env_var("COLUMNS_CSV_PATH", "data/csv/Columns.csv")

image_path = get_env_var("IMAGE_PATH", "data/image/image")
print("\npath:", large_category_csv_path, "\n")
# ファイルパスの絶対パスを構築
product_csv_path = project_root / product_csv_path
large_category_csv_path = project_root / large_category_csv_path
small_category_csv_path = project_root / small_category_csv_path
post_csv_path = project_root / post_csv_path
post_tag_csv_path = project_root / post_tag_csv_path
columns_csv_path = project_root / columns_csv_path
global_image_path = project_root / image_path

print(f"Final product_csv_path: {product_csv_path}")
print(f"File exists: {product_csv_path.exists()}")
print(f"Loaded IMAGE_PATH: {image_path}")
# CSVファイルの読み込み
df_products = pl.read_csv(product_csv_path)
df_large_category = pl.read_csv(
    "../data/csv/Large_category.csv", encoding="utf8"
)
df_small_category = pl.read_csv(
    "../data/csv/Small_category.csv", encoding="utf8"
)
df_posts = pl.read_csv(post_csv_path)
df_post_tags = pl.read_csv(post_tag_csv_path)
df_columns = pl.read_csv(columns_csv_path)

product_blueprint = Blueprint("product", __name__)
category_dict = {
    "モバイル": "mobile",
    "インターネット": "internet",
    "セキュリティ": "security",
    "複合機": "device",
    "サーバー": "server",
    "パソコン": "computer",
    "IoT": "IoT",
    "情報系システム": "system",
    "LED": "LED",
}


@product_blueprint.route("/", methods=["GET"])
@product_blueprint.route("/<product_id>/image", methods=["GET"])
def get_product_image(product_id):
    print("imags")
    product_info = df_products.filter(pl.col("product_id") == product_id).to_dicts()
    if product_info:
        product_info = product_info[0]
        product_id = product_info["product_id"]
        small_category_name = product_info["small_category"]
        large_category_id = df_small_category.filter(
            pl.col("small_category_name") == small_category_name
        )["large_category_id"].to_list()[0]
        large_category_name = df_large_category.filter(
            pl.col("large_category_id") == large_category_id
        )["large_category_name"].to_list()[0]

        large_category_picture = category_dict[large_category_name]
        global global_image_path
        image_path = f"{global_image_path}/{large_category_picture}.jpg"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        try:
            return send_file(image_path, mimetype="image/jpeg")
        except FileNotFoundError:
            return "Image not found", 404
    else:
        return "Product not found", 404


@product_blueprint.route("/<product_id>/info", methods=["GET"])
def get_product_info(product_id):
    print("get_product_info")
    product_info = df_products.filter(pl.col("product_id") == product_id).to_dicts()

    if not product_info:
        return jsonify({"error": "Product not found"}), 404

    product_info = product_info[0]
    product_id = product_info["product_id"]
    product_name = product_info["product_name"]
    description = product_info["description"]
    small_category_name = product_info["small_category"]

    large_category_id = df_small_category.filter(
        pl.col("small_category_name") == small_category_name
    )["large_category_id"].to_list()[0]

    large_category_name = df_large_category.filter(
        pl.col("large_category_id") == large_category_id
    )["large_category_name"].to_list()[0]

    return jsonify(
        {
            "product_id": product_id,
            "product_name": product_name,
            "description": description,
            "small_category_name": small_category_name,
            "large_category_name": large_category_name,
        }
    )


@product_blueprint.route("/<product_id>/post", methods=["GET"])
def get_product_post(product_id):
    print("get_product_post")
    filtered_posts = df_posts.filter(pl.col("product_id") == product_id)
    if not filtered_posts.is_empty():
        temp_posts = filtered_posts.to_dicts()
        post_id = temp_posts[0]["post_id"]
        tag_ids = df_post_tags.filter(pl.col("post_id") == post_id)["tag_id"].to_list()
    else:
        temp_posts = []
        return jsonify({"error": "Column not found"}), 404
    return jsonify(temp_posts)


columns_blueprint = Blueprint("columns", __name__)


@columns_blueprint.route("/<column_id>", methods=["GET"])
def get_column_info(column_id):
    print("get_column_info")
    # コラム情報を取得
    column_info = df_columns.filter(pl.col("column_id") == column_id).to_dicts()

    if not column_info:
        return jsonify({"error": "Column not found"}), 404

    column_info = column_info[0]
    user_id = column_info["user_id"]
    material = column_info["material"]
    created_at = column_info["created_at"]

    # 著者ページのリンクを追加
    user_page_url = f"/user/{user_id}"

    return jsonify(
        {
            "column_id": column_id,
            "user_id": user_id,
            "material": material,
            "created_at": created_at,
            "user_page_url": user_page_url,
        }
    )


# @product_blueprint.route("/<product_id>/column", methods=["GET"])
# product_idに紐づくコラム情報を取得
# def get_product_column(product_id):
#    filtered_posts = df_posts.filter(pl.col("product_id") == product_id)
