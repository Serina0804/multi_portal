import hashlib
import random
from datetime import datetime, timedelta

import numpy as np
import polars as pl

from gpt import (generate_post, generate_product_description,
                 generate_product_name, generate_profile, generate_report)
from module import (compare_datetimes, generate_id, generate_price,
                    generate_random_datetimes, get_large_category, get_name,
                    get_small_category, get_tags, hash_password)

large_category = get_large_category()
small_category = get_small_category()


### 商品テーブル　Products
def Products():
    """
    追加日時, 編集日時, 削除日時追加
    """
    count = 0
    total_count = 37 * 3
    all_id = generate_id(count=total_count, length=10)
    with open("name.txt", "r") as file:
        all_name = [line.strip() for line in file]
    all_category = []
    with open("description.txt", "r") as file:
        all_description = [line.strip() for line in file]
    all_price = generate_price(total_count)
    all_add_time = generate_random_datetimes(total_count)
    all_change_time = generate_random_datetimes(total_count)
    all_delete_time = ["NULL" for i in range(total_count)]
    for i in range(total_count):
        if compare_datetimes(all_add_time[i], all_change_time[i]):
            all_change_time[i] = "NULL"

    for large_key in large_category:
        for small_key in small_category[large_key]:
            for _ in range(3):
                count += 1
                all_category.append(small_key)
                # 名前生成
                if count > len(all_name):
                    if len(all_name) % 3 == 0:
                        all_name.append(generate_product_name(small_key, large_key))
                    elif len(all_name) % 3 == 1:
                        all_name.append(
                            generate_product_name(small_key, large_key, all_name[-1])
                        )
                    elif len(all_name) % 3 == 2:
                        all_name.append(
                            generate_product_name(
                                small_key, large_key, all_name[-1], all_name[-2]
                            )
                        )
                    with open("name.txt", "w") as file:
                        for item in all_name:
                            file.write(f"{item}\n")

                # 商品説明
                if count > len(all_description):
                    all_description.append(generate_product_description(all_name[-1]))
                    with open("description.txt", "w") as file:
                        for item in all_description:
                            file.write(f"{item}\n")
                print("count:", count)

    df = pl.DataFrame(
        {
            "product_id": all_id,
            "product_name": all_name,
            "small_category": all_category,
            "description": all_description,
            "price": all_price,
            "created_at": all_add_time,
            "updated_at": all_change_time,
            "deleted_at": all_delete_time,
        }
    )

    df.write_csv("../csv/Products.csv")


### 大商品カテゴリ Large_category_name
def Large_category_name():
    category_number = [i for i in range(1, 1 + len(large_category))]
    df = pl.DataFrame(
        {"large_category_id": category_number, "large_category_name": category_name}
    )

    df.write_csv("../csv/Large_category_name.csv")


### 小商品カテゴリ Small_category_name
def Small_category_name():
    category_number = [i for i in range(1, 1 + total_number)]
    large_category_df = pl.read_csv("../csv/Large_category_name.csv")

    df = pl.DataFrame(
        {
            "small_category_id": category_number,
            "small_category_name": total_categories,
            "large_category_name": this_categories,
        }
    )
    df = df.join(large_category_df, on="large_category_name", how="right")
    df = df.drop(["large_category_name"])
    df.write_csv("../csv/Small_category_name.csv")


### ユーザテーブル Users
def User():
    total_count = 50
    all_id = generate_id(total_count, 8, id_kind="0123456789")
    all_add_time = generate_random_datetimes(total_count, days=3650)
    all_change_time = generate_random_datetimes(total_count, days=3650)
    all_delete_time = ["NULL" for i in range(total_count)]
    for i in range(total_count):
        if compare_datetimes(all_add_time[i], all_change_time[i]):
            all_change_time[i] = "NULL"
    data = get_name()
    all_name = []
    all_sex = []
    all_email = []
    for name, sex, email in data:
        all_name.append(name)
        all_sex.append(sex)
        all_email.append(email)

    all_occupation = random.choices(
        ["エンジニア", "営業", "営業", "営業"], k=total_count
    )

    # プロフィール文
    all_profile = []
    with open("profile.txt", "r") as file:
        all_profile = [line.strip() for line in file]
    all_calender_id = ["NULL" for i in range(total_count)]
    all_password = [hash_password("password") for i in range(total_count)]

    for i in range(len(all_profile), total_count):
        profile = generate_profile(all_sex[i], all_occupation[i])
        all_profile.append(profile)
        with open("profile.txt", "w") as file:
            for item in all_profile:
                file.write(f"{item}\n")
        print("count:", i)

    df = pl.DataFrame(
        {
            "user_id": all_id,
            "name": all_name,
            "sex": all_sex,
            "email": all_email,
            "occupation": all_occupation,
            "profile": all_profile,
            "password": all_password,
            "calender_id": all_calender_id,
            "created_at": all_add_time,
            "updated_at": all_change_time,
            "deleted_at": all_delete_time,
        }
    )
    df.write_csv("../csv/Users.csv")


#### 日報テーブル Reports
def Reports():
    total_count = 500
    users_table = pl.read_csv("../csv/Users.csv", dtypes={"user_id": pl.Utf8})

    all_id = generate_id(count=total_count, length=10)
    all_user_id = []
    person_id_list = (
        users_table["user_id"].filter(users_table["occupation"] == "営業").to_list()
    )
    all_created_time = sorted(generate_random_datetimes(total_count, days=365))
    all_updated_time = generate_random_datetimes(total_count, days=365)
    all_deleted_time = ["NULL" for i in range(total_count)]
    # all_report = []
    # all_score = []
    with open("report.txt", "r") as file:
        all_report = [line.strip() for line in file]
    with open("report_score.txt", "r") as file:
        all_score = [line.strip() for line in file]
    for i in range(total_count):
        all_user_id.append(person_id_list[i % len(person_id_list)])
    for i in range(len(all_report), total_count):
        if compare_datetimes(all_created_time[i], all_updated_time[i]):
            all_updated_time[i] = "NULL"
        # レポート生成
        (report, score) = generate_report()
        # 報告書記録
        all_report.append(report)
        with open("report.txt", "w") as file:
            for item in all_report:
                file.write(f"{item}\n")
        # スコア記録
        all_score.append(score)
        with open("report_score.txt", "w") as file:
            for item in all_score:
                file.write(f"{item}\n")

    df = pl.DataFrame(
        {
            "report_id": all_id,
            "user_id": all_user_id,
            "material": all_report,
            "created_at": all_created_time,
            "updated_at": all_updated_time,
            "deleted_at": all_deleted_time,
        }
    )
    df.write_csv("../csv/Reports.csv")


### 日報のタグ付けテーブル Report_tags
def Report_tags():
    # CSVファイルを読み込み
    reports_table = pl.read_csv("../csv/Reports.csv")
    tag_table = pl.read_csv("../csv/Tag.csv")

    # post_id と tag_id のリストを取得
    reports_list = reports_table["report_id"].to_list()
    tag_list = tag_table["tag_id"].to_list()

    # リスト内包表記を使って post_id_list と tag_id_list を生成
    report_id_list, tag_id_list = zip(
        *[
            (report_id, tag_id)
            for report_id in reports_list
            for tag_id in random.choices(tag_list, k=random.randint(3, 9))
        ]
    )
    df = pl.DataFrame(
        {
            "report_id": report_id_list,
            "tag_id": tag_id_list,
        }
    )

    df.write_csv("../csv/Report_tags.csv")


### 投稿データテーブル Posts
def Posts():
    total_count = 500
    product_table = pl.read_csv("../csv/Products.csv")
    product_id_list = product_table["product_id"].to_list()

    person_table = pl.read_csv("../csv/Users.csv", dtypes={"user_id": pl.Utf8})
    person_id_list = person_table["user_id"].to_list()

    all_post_id = generate_id(count=total_count, length=12)
    all_product_id = []
    all_parent_id = []
    all_user_id = [random.choice(person_id_list) for _ in range(total_count)]
    with open("comments.txt", "r") as file:
        all_comments = [line.strip() for line in file]
    all_likes_count = [int(np.random.rayleigh(scale=4)) for _ in range(total_count)]

    all_created_at = sorted(generate_random_datetimes(total_count, days=1000))
    all_updated_at = generate_random_datetimes(total_count, days=1000)
    all_deleted_at = generate_random_datetimes(total_count, days=1000)

    for i in range(total_count):
        probability = (i / total_count) * np.random.normal(loc=0, scale=1)
        # 親投稿
        if abs(probability) <= 0.75:
            all_product_id.append(random.choice(product_id_list))
            all_parent_id.append("NULL")
            if compare_datetimes(all_created_at[i], all_updated_at[i]):
                all_updated_at[i] = "NULL"
            # 削除の可能性
            if random.randint(0, 100) > 95:
                if compare_datetimes(all_created_at[i], all_deleted_at[i]):
                    all_deleted_at[i] = "NULL"
            else:
                all_deleted_at[i] = "NULL"
        # 子投稿
        else:
            # 親投稿を決める
            parent = 0
            # 親投稿が削除されていない前提
            while True:
                parent = random.randint(0, i)
                # 投稿が削除されていなく、子投稿でもない
                if all_deleted_at[parent] == "NULL" and all_parent_id[parent] == "NULL":
                    break
            # 親データに準拠
            all_product_id.append(all_product_id[parent])
            all_parent_id.append(all_post_id[parent])
            if compare_datetimes(all_created_at[i], all_updated_at[i]):
                all_updated_at[i] = "NULL"
            # 削除の可能性
            if random.randint(0, 100) > 95:
                if compare_datetimes(all_created_at[i], all_deleted_at[i]):
                    all_deleted_at[i] = "NULL"
            else:
                all_deleted_at[i] = "NULL"

    df = pl.DataFrame(
        {
            "post_id": all_post_id,
            "product_id": all_product_id,
            "parent_id": all_parent_id,
            "user_id": all_user_id,
            "material": all_comments,
            "likes_count": all_likes_count,
            "created_at": all_created_at,
            "updated_at": all_updated_at,
            "deleted_at": all_deleted_at,
        }
    )

    df.write_csv("../csv/Posts.csv")


### 投稿タグテーブル Post_tags
def Post_tags():
    total_count = 500

    post_table = pl.read_csv("../csv/Posts.csv")
    post_id = post_table["post_id"].to_list()
    all_post_id = []

    tag_table = pl.read_csv("../csv/Tag.csv")
    tag_list = []
    all_tag_list = []

    with open("tags.txt", "r") as file:
        all_tags = [list(line.strip().split()) for line in file]
    for items in all_tags:
        tag_list.append(
            tag_table.filter(pl.col("tag_name").is_in(items))["tag_id"].to_list()
        )
    for i in range(total_count):
        for tag_number in tag_list[i]:
            all_post_id.append(post_id[i])
            all_tag_list.append(tag_number)

    # for i in range(len(tags), total_count):
    #     tag_ids.append(random.choices(tag_id_list, k=random.randint(3, 9)))
    #     tags.append(" ".join(tag_table.filter(pl.col("tag_id").is_in(tag_ids[-1]))["tag_name"].to_list()))
    #     comments.append(generate_post(tags[-1]))
    #     print(comments[-1])
    #     # コメントの書き込み
    #     with open("comments.txt", "w") as file:
    #         for item in comments:
    #             file.write(f"{item}\n")
    #     # タグの書き込み
    #     with open("tags.txt", "w") as file:
    #         for item in tags:
    #             file.write(f"{item}\n")
    # CSVファイルを読み込み
    post_table = pl.read_csv("../csv/Posts.csv")
    tag_table = pl.read_csv("../csv/Tag.csv")

    df = pl.DataFrame(
        {
            "post_id": all_post_id,
            "tag_id": all_tag_list,
        }
    )

    df.write_csv("../csv/Post_tags.csv")


### タグテーブル Tag
def Tag():
    tag_name = get_tags()
    tag_number = [i for i in range(1, 1 + len(tag_name))]
    df = pl.DataFrame({"tag_id": tag_number, "tag_name": tag_name})
    df.write_csv("../csv/Tag.csv")

### 売り上げテーブル
def Sales():
    total_count = 1000

    product_table = pl.read_csv("../csv/Products.csv")
    product_id_list = product_table["product_id"].to_list()

    person_table = pl.read_csv("../csv/Users.csv", dtypes={"user_id": pl.Utf8})
    person_id_list = person_table["user_id"].to_list()

    # 売り上げテーブル
    all_sales_id = generate_id(count=total_count, length=14)
    all_user_id = [random.choice(person_id_list) for _ in range(total_count)]
    all_sales = [random.randint(1, 10000)*1000 for _ in range(total_count)]
    all_sale_date = sorted(generate_random_datetimes(total_count, days=365))
    all_created_at = sorted(generate_random_datetimes(total_count, days=365))
    all_deleted_at = ["NULL" for i in range(1000)]

    df_sales = pl.DataFrame(
        {
            "sales_id": all_sales_id,
            "user_id": all_user_id,
            "total_sales": all_sales,
            "sale_date": all_sale_date,
            "created_at": all_created_at,
            "deleted_at": all_deleted_at
        }
    )

    df_sales.write_csv("../csv/Sales.csv")

def Sales_detail():
    sales_id_list = pl.read_csv("../csv/Sales.csv")["sales_id"].to_list()
    product_id_list = pl.read_csv("../csv/Products.csv")["product_id"].to_list()

    all_sales_id = []
    all_product_id = []
    all_quantity = []

    for sale_id in sales_id_list:
        # 売り上げ商品の種類数
        sales_count = random.randint(1, 10)
        sales_product_list = random.choices(product_id_list, k=sales_count)
        sales_product_count = [random.randint(1, 100) for i in range(sales_count)]

        for j in range(sales_count):
            all_sales_id.append(sale_id)
            all_product_id.append(sales_product_list[j])
            all_quantity.append(sales_product_count[j])
        all_detail_id = generate_id(count=len(all_sales_id), length=16)

    df = pl.DataFrame(
        {
            "sales_detail_id": all_detail_id,
            "sales_id": all_sales_id,
            "product_id": all_product_id,
            "quantity": all_quantity
        }
    )

    df.write_csv("../csv/Sales_detail.csv")

def Report_score():
    with open("report_score.txt", "r") as file:
        all_score = [line.strip() for line in file]
    reports_table = pl.read_csv("../csv/Reports.csv")
    report_id_list = reports_table["report_id"].to_list()
    print(len(all_score))
    print(len(report_id_list))

    df = pl.DataFrame(
        {
            "report_id": report_id_list,
            "score": all_score,
        }
    )
    print(df)

    df.write_csv("../csv/Report_score.csv")

Report_score()
    



# ### コラム記事テーブル Columns
# def Columns():
#     total_count = len(article)

#     id_set = set()
#     while True:
#         for i in range(total_count):
#             id_set.add("".join(random.choices(id_kind, k=10)))
#         if len(id_set) != total_count:
#             id_set = set()
#         else:
#             break
#     id_list = list(id_set)

#     person_table = pl.read_csv("../csv/Users.csv", dtypes={"user_id": pl.Utf8})
#     person_id_list = person_table["user_id"].to_list()

#     all_user_id = []
#     for i in range(total_count):
#         all_user_id.append(random.choice(person_id_list))

#     all_created_time = sorted(generate_random_datetimes(total_count, days=365))
#     all_updated_time = ["NULL" for i in range(total_count)]
#     all_deleted_time = ["NULL" for i in range(total_count)]

#     df = pl.DataFrame(
#         {
#             "column_id": id_list,
#             "user_id": all_user_id,
#             "material": article,
#             "created_at": all_created_time,
#             "updated_at": all_updated_time,
#             "deleted_at": all_deleted_time,
#         }
#     )
#     df.write_csv("../csv/Columns.csv")
