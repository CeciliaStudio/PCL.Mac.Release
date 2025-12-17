import hashlib

def sha256_matches(file_path: str, target_hash: str) -> bool:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    file_hash: str = sha256.hexdigest()
    return file_hash.lower() == target_hash.lower()