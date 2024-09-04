# -*- coding: utf-8 -*-
import openai
from flask import Flask, request, jsonify
import random
import polars as pl
from langchain_core.pydantic_v1 import BaseModel, Field
from openai import AzureOpenAI
from langchain_core.output_parsers import JsonOutputParser
import time
import re


# TeamC
api_base = "XXX"
api_version = "XXX"
api_key = "XXX"

deployment_name = "gpt-4o-mini"
model_name = "gpt-4o-mini"

client = AzureOpenAI(api_key=api_key, api_version="XXX", azure_endpoint=api_base)

# お手本レポートの取得
def pickup_good_report(top_reports, this_report, id_set):

    pick_up_set = set()
    count = 0
    while len(pick_up_set) < 3:
        try:
            if count == 0:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f'以下がお手本のレポートの辞書型になります\n{top_reports}\n'
                                + f'この中で今書き上げた{this_report}の内容に近いレポートのidを一つ出力してください\n'
                                + 'ただし、report_idのみ出力してください。'
                            )
                        }
                    ],
                    max_tokens=100,
                    n=1,
                    stop=None,
                    temperature=1.0,
                )
                generated_text = response.choices[0].message.content.strip()
                count += 1
            else:
                number = random.randint(0, len(id_set) - 1)
                pick_up_set.add(list(id_set)[number])

            # 数値に変換を試みる
            if generated_text in id_set:
                pick_up_set.add(generated_text)
            else:
                number = random.randint(0, len(id_set) - 1)
                pick_up_set.add(list(id_set)[number])
            
                
        except Exception as e:
            print(f"Error occurred: {e}")
            number = random.randint(0, len(id_set) - 1)
            pick_up_set.add(list(id_set)[number])
    
    print(pick_up_set)
    return pick_up_set

def feedback_report(this_report):
    """
    みやけえええええええええええええええええええええええええええええええええええええええええええ
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは、管理職の人です。Userには社員が書いた日報が書いてあります。また、【基準】には評価基準が書いてあります。\nUserの内容を読んで、日報の質を【基準】をもとにそれぞれ0から5の間で評価して【フォーマット】に従って整数で回答してください。\nさらに、日報に対するフィードバックを3行程度で書いてください。\n【基準】\n内容：業務内容、本日の課題を書いてある 。\n具体性：業務内容は、何を、どれだけの時間で、どれだけ行なったのかが分かるように書いてある。\n課題：本日の課題をどのように改善するか書いてある。\n\n【フォーマット】\n内容：\n具体性：\n課題：\nフィードバック："
                }, 
                {
                    "role": "user",
                    "content":this_report
                }
            ],
            temperature=0,
            max_tokens=100
        )
        # print(response)
        feedback = response.choices[0].message.content.strip()
        print(feedback)
        # 数字を抽出してint型のリストに変換
        score = [int(num) for num in re.findall(r'内容：(\d+)|具体性：(\d+)|課題：(\d+)', feedback) for num in num if num]
        # score = [random.randint(0, 5) for _ in range(3)]
        feedback_text = re.search(r'フィードバック：(.+)', feedback).group(1)
    except Exception as e:
        print(f"Error in feedback_report: {e}")
        score = [random.randint(0, 5) for _ in range(3)]
        feedback_text = "エラーが発生しました。"
    return (score, feedback_text)

def report_evaluation(input_text, tags, tag_table):
    """投稿レポートの評価を行う"""
    try:
        # タグの生成
        tag_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"以下のタグテーブル{tags}から{input_text}にふさわしいタグをidでリスト型で取得して"
                },
                {"role": "user", "content": input_text}
            ],
            temperature=0,
            max_tokens=100
        )
        generated_tags = tag_response.choices[0].message.content.strip().split("、")

        # スコアの生成
        score_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"{input_text}に点数をつけて"
                },
                {"role": "user", "content": input_text}
            ],
            temperature=0,
            max_tokens=100
        )
        generated_score = score_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in report_evaluation: {e}")
        tag_number_list = tag_table["tag_id"].to_list()
        choice_number = random.randint(3, 10)
        generated_tags = random.choices(tag_number_list, k=choice_number)
        generated_score = random.randint(0, 10)
    return (generated_tags, generated_score)

def generate_tags(input_text):
    """コラムの内容に適切なタグを生成する"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "【タグ一覧】にタグがあります。\nまた、Userは分類してもらいたいコラムの内容です。\n【タグ一覧】からUserの内容に適切なタグを選んでつけてください。ただし、【タグ一覧】は「ジャンル」によって分類されています。1つの「ジャンル」から選ぶのは1つまでにしてください。ただし、複数の「ジャンル」から選択しても構いません。また、出力は「、」区切りの単語で答えてください。ただし、出力単語が1つの場合は、1つの単語のみを出力してください。\n\n【タグ一覧】\n「ジャンル」：商材関連\n・新商品\n・既存商品\n・サービス\n\n「ジャンル」：業界別\n・IT\n・製造業\n・医療\n・介護\n\n「ジャンル」：スキルアップ\n・プレゼンテーション\n・交渉\n・時事ネタ\n・トレンド\n\n「ジャンル」：社内コラボレーション\n・部署間連携\n・プロジェクト\n・成功事例\n・失敗事例\n"
                },
                {"role": "user", "content": input_text}
            ],
            temperature=0.5,
            max_tokens=100
        )
        generated_tags = response.choices[0].message.content.strip().split("、")
    except Exception as e:
        print(f"Error in generate_tags: {e}")
        generated_tags = []
    return generated_tags

def generate_user_tags(input_text):
    """社員の経歴に適切なタグを生成する"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "【タグ一覧】にタグがあります。\nまた、Userは社員の経歴です。\n【タグ一覧】からUserの経歴に適切なタグを選んでつけてください。\nただし、【タグ一覧】は「ジャンル」によって分類されています。1つの「ジャンル」から選ぶのは1つまでにしてください。ただし、複数の「ジャンル」から選択しても構いません。また、出力は「、」区切りの単語で答えてください。ただし、出力単語が1つの場合は、1つの単語のみを出力してください。\n【タグ一覧】\n「ジャンル」：年度\n・新人\n・若年層\n・中堅\n・ベテラン\n\n「ジャンル」：業界の強み\n・IT業界\n・製造業界\n・医療業界\n・介護業界\n・不動産業界\n・化粧品業界\n\n「ジャンル」：職種\n・エンジニア\n・営業部\n・人事部\n\n「ジャンル」：スキルセット\n・データ分析\n・プロジェクト管理\n・Python\n"
                },
                {"role": "user", "content": input_text}
            ],
            temperature=0,
            max_tokens=100
        )
        generated_tags = response.choices[0].message.content.strip().split("、")
    except Exception as e:
        print(f"Error in generate_user_tags: {e}")
        generated_tags = []
    return generated_tags

# 使用例
# input_text = "このコラムでは、新しい商品の一覧をお届けします。"
# print(generate_tags(input_text))
# input_text = "クライアントから前向きな反応が得られました。"
# print(report_evaluation(input_text))

