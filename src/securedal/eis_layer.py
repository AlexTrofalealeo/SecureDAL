from abc import ABC, abstractmethod
from .mapping import AnchorMapping, SQLiteAnchorMapping
import ipfshttpclient
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Any

PINATA_API = "https://api.pinata.cloud"

class EISLayer(ABC):
    """Abstract base class for the External Immutable Storage layer.
    Implement this to use a different immutable store instead of IPFS."""

    @abstractmethod
    def store_hash(self, key: str, hash_value: bytes) -> str:
        """Store a hash anchor. Returns an identifier (e.g. CID) for the stored anchor."""
        ...

    @abstractmethod
    def get_hash(self, key: str) -> bytes | None:
        """Retrieve the hash anchor for a key. Returns None if not found."""
        ...

    @abstractmethod
    def delete_hash(self, key: str) -> None:
        """Delete the hash anchor for a key."""
        ...

    def close(self) -> None:
        """Optional cleanup."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

class IPFSEISLayer(EISLayer):
    """Default IPFS-based EIS layer."""

    def __init__(
        self, 
        address: str = "/ip4/127.0.0.1/tcp/5001", 
        mapping_path: str = "./storage/mapping/tamper_mapping.db",
        pinata_token: str = None,
        backend_context: dict[str, Any] = None,
        mapping: AnchorMapping = None,  # optional custom mapping
    ) -> None:
        self._backend_context = backend_context
        self._mapping = mapping or SQLiteAnchorMapping(mapping_path) # key->CID mapping
        self._client = ipfshttpclient.Client(addr=address, session=True)

        # Executor for async pinata pinning
        self._executor = ThreadPoolExecutor(max_workers=8) if pinata_token else None
        self._pinata_token = pinata_token

    def _full_key(self, key: str) -> str:
        return self._backend_context["id"] + key

    def store_hash(self, key: str, hash_value: bytes) -> str:
        cid = self._client.add_bytes(hash_value)
        self._client.pin.add(cid)

        self._mapping.set(self._full_key(key), cid)

        if self._pinata_token:
            future = self._executor.submit(self._pin_to_pinata, hash_value)
            future.add_done_callback(self._handle_pin_error)

        return cid

    def get_hash(self, key: str) -> tuple[bool, bytes | None]:        

        cid = self._mapping.get(self._full_key(key))
        if cid is None:
            return False, None # Mapping not found
        
        try:
            hash_value = self._client.cat(cid)
        except ipfshttpclient.exceptions.TimeoutError: # To identify a timeout error as a missing anchor
            return True, None # Mapping found, anchor not found  

        return True, hash_value # Mapping found, anchor may be found

    def delete_hash(self, key: str) -> None:
        cid = self._mapping.delete(self._full_key(key))
        if cid:
            try:
                self._client.pin.rm(cid)
            except Exception:
                pass

            if self._pinata_token:
                self._executor.submit(self._unpin_pinata, cid)

    def _pin_to_pinata(self, hash_value: bytes) -> None:
        response = requests.post(
            f"{PINATA_API}/pinning/pinFileToIPFS",
            files={"file": ("anchor", hash_value)},
            headers={"Authorization": f"Bearer {self._pinata_token}"},
        )
        response.raise_for_status()
    
    """ def _pin_by_hash_pinata(self, cid: str) -> None:
        response = requests.post(
            f"{PINATA_API}/pinning/pinByHash",
            json={"hashToPin": cid},
            headers={"Authorization": f"Bearer {self._pinata_token}"},
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text}")
        response.raise_for_status() """

    def _unpin_pinata(self, cid: str) -> None:
        response = requests.delete(
            f"{PINATA_API}/pinning/unpin/{cid}",
            headers={"Authorization": f"Bearer {self._pinata_token}"},
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
        if self._client:
            self._client.close()
        self._mapping.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

