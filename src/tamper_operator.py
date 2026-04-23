import opendal
import hashlib
from typing import Any
from .eis_layer import EISLayer
from .exceptions import BulkTamperException, TamperDetectedException, MissingAnchorException, DataNotFoundException, TamperException

_IDENTITY_KEYS = {
    "bucket", "container", "filesystem", "share_name",
    "endpoint", "root", "region", "db",
    "database", "collection", "table", "repo_id",
    "key_field", "value_field",
    "space", "repository", "branch",         # nebula, lakefs
    "datadir", "datafile",                   # local/embedded DBs
    "namespace",                             # surrealdb
    "owner", "repo",                         # github
    "drive_type",                            # aliyun_drive
}

class TamperOperator:
    operator: opendal.Operator
    ledger: EISLayer

    def __init__(
            self, 
            scheme: str, 
            ledger: str = "/ip4/127.0.0.1/tcp/5001", 
            mapping_path: str = "./storage/mapping/tamper_mapping.db", 
            pinata_token: str = None, 
            **kwargs: Any
        ) -> None:

        self.operator = opendal.Operator(scheme, **kwargs)
        self.ledger = EISLayer(
            address=ledger,
            mapping_path=mapping_path,
            pinata_token=pinata_token,
        )

        operator_details = {"scheme": scheme}
        operator_details.update({k: v for k, v in kwargs.items() if k in _IDENTITY_KEYS})
        self.operator_context = "&".join(f"{k}={v}" for k, v in sorted(operator_details.items()))

    @staticmethod
    def _normalize_key(key: str) -> str:
        return key.lstrip("/")

    def write(self, key: str, data: bytes, **options: Any) -> None:
        key = self._normalize_key(key)
        if options.get("append", False) and self.operator.capability().write_can_append:
            try:
                existing_data = self.read(key)
            except opendal.exceptions.NotFound:
                pass
            
            full_data = (existing_data or b"") + data
        else:
            full_data = data

        self.operator.write(key, data, **options)

        metadata = self.operator.stat(key)
        hash_value = compute_hash(key, full_data, metadata, self.operator_context)
        self.ledger.store_hash(key, hash_value)

    def read(self, key: str, **options: Any) -> bytes:
        key = self._normalize_key(key)
        expected_hash = self.ledger.get_hash(key)
        
        try:
            data = self.operator.read(key, **options)
        except opendal.exceptions.NotFound:
            if expected_hash is not None:
                raise DataNotFoundException(key)
            raise
        
        if expected_hash is None:
            raise MissingAnchorException(key)
        
        metadata = self.operator.stat(key)
        current_hash = compute_hash(key, data, metadata, self.operator_context)
        if expected_hash != current_hash:
            raise TamperDetectedException(key)

        return data
    
    def delete(self, key: str) -> None:
        key = self._normalize_key(key)
        self.operator.delete(key)
        self.ledger.delete(key)

    def copy(self, source: str, dest: str) -> None:
        source = self._normalize_key(source)
        dest = self._normalize_key(dest)
        data = self.read(source)
        self.operator.copy(source, dest)
        metadata = self.operator.stat(dest)
        hash_value = compute_hash(dest, data, metadata, self.operator_context)
        self.ledger.store_hash(dest, hash_value)

    def rename(self, source: str, dest: str) -> None:
        source = self._normalize_key(source)
        dest = self._normalize_key(dest)
        data = self.read(source)
        self.operator.rename(source, dest)
        metadata = self.operator.stat(dest)
        hash_value = compute_hash(dest, data, metadata, self.operator_context)
        self.ledger.store_hash(dest, hash_value)
        self.ledger.delete(source)

    def remove_all(self, path: str) -> None:
        entries = list(self.operator.list(path))
        
        self.operator.remove_all(path)
        
        for entry in entries:
            if entry.metadata.mode.is_file():
                self.ledger.delete(entry.path)

    def read_all(self, path: str = "/") -> dict[str, bytes]:
        results: dict[str, bytes] = {}
        violations: dict[str, TamperException] = {}

        for entry in self.operator.list(path):
            if not entry.metadata.mode.is_file():
                continue

            key = entry.path
            try:
                results[key] = self.read(key)
            except TamperException as e:
                violations[key] = e

        if violations:
            raise BulkTamperException(violations=violations, results=results)

        return results
    

    def open(self, *args, **kwargs):
        raise NotImplementedError(
            "TamperOperator does not support 'open()'. Use read/write instead."
        )

    def __getattr__(self, name):
        return getattr(self.operator, name)
    
    def close(self) -> None:
        self.ledger.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
    

def compute_hash(key: str, data: bytes, metadata: opendal.Metadata, operator_context: str) -> bytes:
    meta_parts = []
    if metadata.content_length is not None:
        meta_parts.append(f"content_length={metadata.content_length}")
    if metadata.last_modified is not None:
        meta_parts.append(f"last_modified={metadata.last_modified.isoformat()}")
    if metadata.etag is not None:
        meta_parts.append(f"etag={metadata.etag}")
    if metadata.version is not None:
        meta_parts.append(f"version={metadata.version}")
    meta_str = "&".join(meta_parts)

    payload = operator_context.encode() + key.encode() + data + meta_str.encode()
    return hashlib.sha256(payload).digest()