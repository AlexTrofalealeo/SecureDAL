import ipfshttpclient
import requests
import sqlite3
from concurrent.futures import ThreadPoolExecutor

PINATA_API = "https://api.pinata.cloud"

class EISLayer:

    def __init__(
        self, 
        address: str = "/ip4/127.0.0.1/tcp/5001", 
        mapping_path: str = "./storage/mapping/tamper_mapping.db",
        pinata_token: str = None,
    ) -> None:
        self.db = sqlite3.connect(mapping_path, check_same_thread=False) # key->CID mapping
        self._init_db()
        
        self.client = ipfshttpclient.Client(addr=address, session=True)

        # Executor for async pinata pinning
        self._executor = ThreadPoolExecutor(max_workers=8) if pinata_token else None

        self.pinata_token = pinata_token

    def _init_db(self) -> None:
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS mapping (
                key  TEXT PRIMARY KEY,
                cid  TEXT NOT NULL
            )
        """)
        self.db.commit()

    def _persist_mapping(self, key: str, cid: str) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO mapping (key, cid) VALUES (?, ?)",
            (key, cid)
        )
        self.db.commit()

    def _get_cid_from_mapping(self, key: str) -> str | None:
        row = self.db.execute(
            "SELECT cid FROM mapping WHERE key = ?", (key,)
        ).fetchone()

        if row:
            return row[0]
        
    def _delete_key_from_mapping(self, key: str) -> str | None:
        row = self.db.execute(
            "SELECT cid FROM mapping WHERE key = ?", (key,)
        ).fetchone()

        if row:
            self.db.execute("DELETE FROM mapping WHERE key = ?", (key,))
            self.db.commit()
            return row[0]

    def store_hash(self, key: str, hash_value: bytes) -> str:
        cid = self.client.add_bytes(hash_value)
        self.client.pin.add(cid)

        self._persist_mapping(key, cid)

        if self.pinata_token:
            future = self._executor.submit(self._pin_to_pinata, hash_value)
            future.add_done_callback(self._handle_pin_error)

        return cid

    def get_hash(self, key: str) -> bytes | None:        

        cid = self._get_cid_from_mapping(key)
        if cid is None:
            return None

        return self.client.cat(cid)

    def delete(self, key: str) -> None:
        cid = self._delete_key_from_mapping(key)

        if cid:
            try:
                self.client.pin.rm(cid)
            except Exception:
                pass

            if self.pinata_token:
                self._executor.submit(self._unpin_pinata, cid)

    def _pin_to_pinata(self, hash_value: bytes) -> None:
        response = requests.post(
            f"{PINATA_API}/pinning/pinFileToIPFS",
            files={"file": ("anchor", hash_value)},
            headers={"Authorization": f"Bearer {self.pinata_token}"},
        )
        response.raise_for_status()
    
    """ def _pin_by_hash_pinata(self, cid: str) -> None:
        response = requests.post(
            f"{PINATA_API}/pinning/pinByHash",
            json={"hashToPin": cid},
            headers={"Authorization": f"Bearer {self.pinata_token}"},
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text}")
        response.raise_for_status() """

    def _unpin_pinata(self, cid: str) -> None:
        response = requests.delete(
            f"{PINATA_API}/pinning/unpin/{cid}",
            headers={"Authorization": f"Bearer {self.pinata_token}"},
        )
        response.raise_for_status()

    def _handle_pin_error(self, future) -> None:
        try:
            future.result()
        except Exception as e:
            print(f"Async Pinata pin failed: {e}")

    def close(self) -> None:
        if self._executor:
            self._executor.shutdown(wait=True)
        if self.client:
            self.client.close()
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

