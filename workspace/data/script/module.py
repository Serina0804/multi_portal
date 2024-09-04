import numpy as np
import random
from datetime import datetime, timedelta
import hashlib

def generate_price(n, sigma=200):
    prices = []
    for _ in range(n):
        value = np.random.rayleigh(sigma)
        value_clipped = np.clip(value, 1, 1000)
        prices.append(int(value_clipped) * 100)
    return prices

def get_large_category():
    # 大カテゴリ
    category_name = [
        "モバイル",
        "インターネット",
        "セキュリティ",
        "複合機",
        "サーバー",
        "パソコン",
        "IoT",
        "情報系システム",
        "LED",
    ]

    return category_name

def get_small_category():
    # 小カテゴリ
    categories = {
        "モバイル": {
            "スマートフォン",
            "タブレット",
            "ウェアラブルデバイス",
            "モバイルアクセサリー",
            "SIMカード",
        },
        "インターネット": {
            "ブロードバンド",
            "Wi-Fiサービス",
            "クラウドストレージ",
            "VPNサービス",
            "Webホスティング",
        },
        "セキュリティ": {
            "アンチウイルス",
            "ファイアウォール",
            "セキュリティカメラ",
            "マルウェア対策",
        },
        "複合機": {"オフィス用複合機", "プリンター", "スキャナー", "ファクシミリ"},
        "サーバー": {
            "ファイルサーバー",
            "メールサーバー",
            "データベースサーバー",
            "ウェブサーバー",
        },
        "パソコン": {"デスクトップPC", "ノートPC", "ゲーミングPC", "ビジネスPC"},
        "IoT": {
            "スマートホームデバイス",
            "スマートウォッチ",
            "スマートスピーカー",
            "IoTセンサー",
        },
        "情報系システム": {
            "ERPシステム",
            "CRMシステム",
            "データ分析システム",
            "ビジネスインテリジェンス",
        },
        "LED": {"LED照明", "LEDディスプレイ", "LED電球"},
    }
    return categories

def generate_random_datetimes(n, days=365):
    now = datetime.now()
    year_ago = now - timedelta(days=days)
    random_datetimes = [
        (year_ago + timedelta(seconds=random.randint(0, days * 24 * 3600))).strftime(
            "%Y-%m-%d %H:%M"
        ) for i in range(n)
    ]
    return random_datetimes


def compare_datetimes(dt_str1, dt_str2):
    datetime1 = datetime.strptime(dt_str1, "%Y-%m-%d %H:%M")
    datetime2 = datetime.strptime(dt_str2, "%Y-%m-%d %H:%M")

    if datetime1 > datetime2:
        return True
    else:
        return False
    

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hashed_password = hash_object.hexdigest()
    
    return hashed_password

def generate_id(count, length,  id_kind = "0123456789QWERTYUIOPASDFGHJKLZXCVBNM"):
    id_set = set()
    while True:
        for i in range(count):
            id_set.add("".join(random.choices(id_kind, k=length)))
        if len(id_set) != count:
            id_set = set()
        else:
            return list(id_set)
        
def get_name():
    names_with_gender_and_email = [("田中 太郎", "男性", "tanaka.taro@otsuka.co.jp"), ("鈴木 花子", "女性", "suzuki.hanako@otsuka.co.jp"), ("佐藤 次郎", "男性", "sato.jiro@otsuka.co.jp"), ("高橋 美咲", "女性", "takahashi.misaki@otsuka.co.jp"), ("伊藤 勇気", "男性", "ito.yuki@otsuka.co.jp"), ("山本 真由美", "女性", "yamamoto.mayumi@otsuka.co.jp"), ("中村 健一", "男性", "nakamura.kenichi@otsuka.co.jp"), ("小林 彩香", "女性", "kobayashi.ayaka@otsuka.co.jp"), ("加藤 隆", "男性", "kato.takashi@otsuka.co.jp"), ("吉田 真由子", "女性", "yoshida.mayuko@otsuka.co.jp"), ("山田 直人", "男性", "yamada.naoto@otsuka.co.jp"), ("渡辺 結衣", "女性", "watanabe.yui@otsuka.co.jp"), ("松本 大輔", "男性", "matsumoto.daisuke@otsuka.co.jp"), ("井上 裕子", "女性", "inoue.yuko@otsuka.co.jp"), ("木村 明", "男性", "kimura.akira@otsuka.co.jp"), ("清水 優子", "女性", "shimizu.yuko@otsuka.co.jp"), ("山崎 一郎", "男性", "yamazaki.ichiro@otsuka.co.jp"), ("斎藤 智子", "女性", "saito.tomoko@otsuka.co.jp"), ("中川 優", "男性", "nakagawa.yu@otsuka.co.jp"), ("森本 真央", "女性", "morimoto.mao@otsuka.co.jp"), ("原田 健", "男性", "harada.ken@otsuka.co.jp"), ("橋本 あかり", "女性", "hashimoto.akari@otsuka.co.jp"), ("藤田 美穂", "女性", "fujita.miho@otsuka.co.jp"), ("川口 剛", "男性", "kawaguchi.tsuyoshi@otsuka.co.jp"), ("石田 晴美", "女性", "ishida.harumi@otsuka.co.jp"), ("小川 貴之", "男性", "ogawa.takayuki@otsuka.co.jp"), ("前田 美奈子", "女性", "maeda.minako@otsuka.co.jp"), ("田辺 亮太", "男性", "tanabe.ryota@otsuka.co.jp"), ("後藤 愛", "女性", "goto.ai@otsuka.co.jp"), ("藤井 亮", "男性", "fujii.ryo@otsuka.co.jp"), ("杉本 美紀", "女性", "sugimoto.miki@otsuka.co.jp"), ("三浦 和也", "男性", "miura.kazuya@otsuka.co.jp"), ("村上 朋子", "女性", "murakami.tomoko@otsuka.co.jp"), ("岡田 翔", "男性", "okada.sho@otsuka.co.jp"), ("藤原 理恵", "女性", "fujiwara.rie@otsuka.co.jp"), ("松井 圭介", "男性", "matsui.keisuke@otsuka.co.jp"), ("上田 千尋", "女性", "ueda.chihiro@otsuka.co.jp"), ("横山 大地", "男性", "yokoyama.daichi@otsuka.co.jp"), ("永井 佳奈", "女性", "nagai.kana@otsuka.co.jp"), ("石川 智也", "男性", "ishikawa.tomoya@otsuka.co.jp"), ("中田 彩", "女性", "nakata.aya@otsuka.co.jp"), ("森田 健二", "男性", "morita.kenji@otsuka.co.jp"), ("浜田 純", "男性", "hamada.jun@otsuka.co.jp"), ("竹内 和美", "女性", "takeuchi.kazumi@otsuka.co.jp"), ("山内 拓", "男性", "yamauchi.taku@otsuka.co.jp"), ("池田 美和", "女性", "ikeda.miwa@otsuka.co.jp"), ("今井 亮", "男性", "imai.ryo@otsuka.co.jp"), ("黒田 志穂", "女性", "kuroda.shiho@otsuka.co.jp"), ("西村 智", "男性", "nishimura.satoshi@otsuka.co.jp"), ("原 宏美", "女性", "hara.hiromi@otsuka.co.jp")]
    return names_with_gender_and_email

def get_tags():
    tag_name = [
        "Q&A", "商品知識", "新商品", "既存商品", "サービス", "IT", "製造業", "医療", "金融", "流通", "薬品", "介護", 
        "プレゼンテーション", "交渉", "時事ネタ", "トレンド", "部署間連携", "プロジェクト", "成功事例", "失敗事例",
        "顧客対応", "フォローアップ", "リード", "クロージング", "マーケティング", "競合分析", "課題解決", 
        "教育・トレーニング", "イベント", "顧客満足度", "コスト削減", "技術サポート", "法律・規制", "サプライチェーン", 
        "品質管理", "イノベーション", "生産性向上", "顧客ニーズ", "提案書", "コラボレーション"
    ]
    return tag_name