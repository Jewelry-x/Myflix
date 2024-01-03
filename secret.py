from hashlib import sha256

def hash_password(password):
        # Your password hashing logic here
        sha256_hash = sha256()
        sha256_hash.update(password.encode('utf-8'))
        return sha256_hash.hexdigest()