import openai
import random

# Azure OpenAI Serviceの設定
api_base = "XXX"  # あなたのエンドポイント
api_version = "XXX"  # 使用するAPIバージョンを設定
api_key = "XXX"  # あなたのAPIキー


# APIキーとエンドポイントを設定
openai.api_key = api_key
openai.api_base = api_base
openai.api_version = api_version
openai.api_type = "azure"


def generate_product_name(small_category, large_category, last_name = "", last = ""):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": large_category
                + "のサブカテゴリである"
                + small_category
                + "の新しい製品のユニークな名前を1つ生成し、生成した名前のみを教えてください。名前は"
                + small_category
                + "カテゴリの製品のタイプを明確に反映するものでなければなりません。キャッチーで関連性のある製品名を提供してください。"
                "ただし、" + last_name + "や" + last + "とは異なる名前でお願いします",
            }
        ],
        temperature=0.5,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # 生成されたtextを取得
    generated_text = response["choices"][0]["message"]["content"].strip()
    return generated_text


def generate_product_description(product_name):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": product_name
                + "という商品の仕様説明、用途の情報を入れたひとまとめの文章を作ってください。ただし、文章は5行程度にしてください。ただし、その情報の中には、その商品ならではのポイントや、どのようなシチュエーションでお勧めできるかも含めてください。",
            }
        ],
        temperature=0.5,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # 生成されたtextを取得
    generated_text = response["choices"][0]["message"]["content"].strip()
    return generated_text

def generate_profile(sex, occupation):
    age = random.randint(1, 30)
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": f'性別: {sex}, 職種: {occupation}, 勤務年数: {age}の社員がいるとします。会社はSIerであるとします。'
                 + '職種に着目しながら、強みや趣味などを挙げながら社内SNSでのプロフィール文を作成して下さい。ただし、文章は2-3行程度にしてください。また、性別や名前は書かなくでも結構です。'
            }
        ],
        temperature=0.5,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # 生成されたtextを取得
    generated_text = response["choices"][0]["message"]["content"].strip()
    return generated_text

def generate_report():
    score = random.randint(0, 10)
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
            "role": "system",
            "content": [
                {
                "text": f'あなたは、営業部の社員です。これから日報を作成してください。\nただし、【注意点】に従って【フォーマット】を参考にしてください。\nただし、【フォーマット】はUserに入っています。\n\n【注意点】\n・改行はしないでください\n・【フォーマット】に従ってください。\n・固有名詞に関してはABC以外で日本の会社で実在するものにしてください。\n・日報入力は、お客様との商談内容の要点を簡潔、具体的に入力をしてください。\n・いつ、誰と、どこで、何について商談をして、なぜ、どのように(5W1H)を意識してください。\n・商談情報は会社にとっての大切な「資産」です。数年後に誰が読んでもわかるように入力することを意識してください。\n・担当者がわかる場合は、必ず面談した担当者を選択、登録してください。ただし、作成する日報は完璧なものを10点、フォーマットに全く従っていないものを0点として、{score}点のものを出力してください',
                "type": "text"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "text": "_企業名：_訪問時間：_訪問目的（初回訪問、精査、提案、クローズ、関係構築、フォロー、納品など）：_同行者名：_お客様の課題：_次回訪問日程：_次回訪問目的（上記の訪問目的と同項目）：_フリーフォーマット：",
                "type": "text"
                }
            ]
            }
        ],
        temperature=0.5,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # 生成されたtextを取得
    generated_text = response["choices"][0]["message"]["content"].strip()
    return (generated_text, score)

def generate_post(tags):
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",  # デプロイ名（またはエンジン名）
        messages=[
            {
                "role": "system",
                "content": f'あなたは営業で商品の宣伝をしています。以下のタグ情報{tags}を含めた商品の営業に関するレビューを作成してください'
                 + '\n作成する際は以下の点に注意してください\n-営業の視点に立って商品をレビューすること\n-すべてのタグ情報に関連したものであれば問題ない\n-2-3行で出力すること'
            }
        ],
        temperature=0.5,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # 生成されたtextを取得
    generated_text = response["choices"][0]["message"]["content"].strip()
    return generated_text


