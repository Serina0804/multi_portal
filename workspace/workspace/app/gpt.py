# -*- coding: utf-8 -*-
import openai
from flask import Flask, request, jsonify


# Azure OpenAI Serviceの設定
api_base = "XXX"  # あなたのエンドポイント
api_version = "XXX"  # 使用するAPIバージョンを設定
api_key = "XXX"  # あなたのAPIキー


# APIキーとエンドポイントを設定
openai.api_key = api_key
openai.api_base = api_base
openai.api_version = api_version
openai.api_type = "azure"

def generate_tags(input_text):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": "【タグ一覧】にタグがあります。\nまた、Userは分類してもらいたいコラムの内容です。\n【タグ一覧】からUserの内容に適切なタグを選んでつけてください。ただし、【タグ一覧】は「ジャンル」によって分類されています。1つの「ジャンル」から選ぶのは1つまでにしてください。ただし、複数の「ジャンル」から選択しても構いません。また、出力は「、」区切りの単語で答えてください。ただし、出力単語が1つの場合は、1つの単語のみを出力してください。\n\n【タグ一覧】\n「ジャンル」：商材関連\n・新商品\n・既存商品\n・サービス\n\n「ジャンル」：業界別\n・IT\n・製造業\n・医療\n・介護\n\n「ジャンル」：スキルアップ\n・プレゼンテーション\n・交渉\n・時事ネタ\n・トレンド\n\n「ジャンル」：社内コラボレーション\n・部署間連携\n・プロジェクト\n・成功事例\n・失敗事例\n"
                
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0.5,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # 生成されたタグを取得
    generated_tags = response['choices'][0]['message']['content'].strip().split('、')
    return generated_tags

def generate_user_tags(input_text):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": "【タグ一覧】にタグがあります。\nまた、Userは社員の経歴です。\n【タグ一覧】からUserの経歴に適切なタグを選んでつけてください。\nただし、【タグ一覧】は「ジャンル」によって分類されています。1つの「ジャンル」から選ぶのは1つまでにしてください。ただし、複数の「ジャンル」から選択しても構いません。また、出力は「、」区切りの単語で答えてください。ただし、出力単語が1つの場合は、1つの単語のみを出力してください。\n【タグ一覧】\n「ジャンル」：年度\n・新人\n・若年層\n・中堅\n・ベテラン\n\n「ジャンル」：業界の強み\n・IT業界\n・製造業界\n・医療業界\n・介護業界\n・不動産業界\n・化粧品業界\n\n「ジャンル」：職種\n・エンジニア\n・営業部\n・人事部\n\n「ジャンル」：スキルセット\n・データ分析\n・プロジェクト管理\n・Python\n\n"
                
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # 生成されたタグを取得
    generated_tags = response['choices'][0]['message']['content'].strip().split('、')
    return generated_tags


def report_evaluation(input_text):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": "あなたは、管理職の人です。Userには社員が書いた日報が書いてあります。\nUserの内容を読んで、日報の質を0.0から5.0の間で評価してください。ただし、小数点第一位までで表示してください。\n【基準】には評価基準が書いてあります。【基準】を参考にして、評価点数だけを教えてください。\n\n【基準】\n・業務内容、本日の課題を書いてある \n・業務内容は、何を、どれだけの時間で、どれだけ行なったのかが分かるように書く\n・業務内容は、数字や固有名詞を入れ、誰が見ても同じ理解ができるように書く\n・課題は、「～と思いました」で終わらないようにする \n・課題は、指導してくれた先輩への感謝の気持ちや、明日から頑張ることなど、一文を添えるとなお良い（ただし書きすぎないこと）"
                
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    # 生成されたタグを取得
    generated_tags = response['choices'][0]['message']['content'].strip().split('、')
    return generated_tags


# 使用例
# input_text = "このコラムでは、新しい商品の一覧をお届けします。"
# print(generate_tags(input_text))
input_text = "クライアントから前向きな反応が得られました。"
print(report_evaluation(input_text))
