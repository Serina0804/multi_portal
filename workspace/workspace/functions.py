import hashlib
import random

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    hashed_password = hash_object.hexdigest()
    return hashed_password

def generate_new_id(id_list, count, length, id_kind="0123456789QWERTYUIOPASDFGHJKLZXCVBNM"):
    id_set = set(id_list)
    new_id_set = set()
    
    # 重複を避けてIDを生成する
    while len(new_id_set) < count:
        new_id = "".join(random.choices(id_kind, k=length))
        if new_id not in id_set and new_id not in new_id_set:
            new_id_set.add(new_id)

    return list(new_id_set)
