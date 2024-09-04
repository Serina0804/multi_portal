import numpy as np
def generate_single_rayleigh_value(sigma=200):
    # レイリー分布から1個のデータを生成
    value = np.random.rayleigh(sigma)
    
    # 値を1から1000の範囲にクリップ
    value_clipped = np.clip(value, 1, 1000)
    
    return int(value_clipped)*100

print(generate_single_rayleigh_value())