from .eis_layer import EISLayer
from .exceptions import BulkTamperException, TamperDetectedException, MissingAnchorException, DataNotFoundException, TamperException
import opendal
from typing import Any
from hashlib import sha256
import json
from pathlib import PurePosixPath

_IDENTITY_KEYS = {
    "bucket": "str", "container": "str", "filesystem": "str", "share_name": "str",
    "endpoint": "sre", "region": "str", "db": "int",
    "database": "str", "collection": "str", "table": "str", "repo_id": "str",
    #"key_field": "str", "value_field": "str",
    "space": "str", "repository": "str", "branch": "str",         # nebula, lakefs
    "datadir": "path", "datafile": "path",                   # local/embedded DBs
    "namespace": "str",                             # surrealdb
    "owner": "str", "repo": "str",                         # github
    "drive_type": "str",                            # aliyun_drive
    "root": "path", "atomic_write_dir": "path",
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
        self.operator_context = self._build_operator_context(scheme, **kwargs)

        self.ledger = EISLayer(
            address=ledger,
            mapping_path=mapping_path,
            pinata_token=pinata_token,
            backend_context=self.operator_context,
        )

    @classmethod
    def _build_operator_context(cls, scheme: str, **kwargs: Any) -> str:

        def _normalize(v):
            if isinstance(v, bool):
                return str(v).lower()
            if isinstance(v, (int, float)):
                return str(v)
            return str(v).strip()
        
        paths = {
            k: cls._normalize_path(kwargs[k]) 
            for k, t in _IDENTITY_KEYS.items() 
            if t == "path" and k in kwargs and kwargs[k]
        }
        base_path = "/".join(paths.values())

        canonical = json.dumps(
            {
                k: _normalize(kwargs[k])
                for k, t in sorted(_IDENTITY_KEYS.items())
                if t != "path" and k in kwargs and kwargs[k]
            },
            separators=(",", ":"),
        )
        digest = sha256(canonical.encode()).hexdigest()[:16]
        context_id = f"{scheme}:{digest}:{base_path}/" if base_path else f"{scheme}:{digest}:"

        return {
            "id": context_id,
            "raw": canonical, 
            "path": base_path, 
        }

    @staticmethod
    def _normalize_path(path: str) -> str:
        if path is None:
            return ""
        p = str(path).strip()
        p = p.replace("\\", "/")        
        p = str(PurePosixPath(p))        
        p = p.lstrip("/")
        return "" if p=="." else p

    def write(self, key: str, data: bytes, **options: Any) -> None:
        key = self._normalize_path(key)
        if options.get("append", False) and self.operator.capability().write_can_append:
            try:
                existing_data = self.read(key)
            except opendal.exceptions.NotFound:
                pass
            
            full_data = (existing_data or b"") + data
        else:
            full_data = data

        self.operator.write(key, data, **options)

        hash_value = self._compute_hash(full_data)
        self.ledger.store_hash(key, hash_value)

    def read(self, key: str, **options: Any) -> bytes:
        key = self._normalize_path(key)
        expected_hash = self.ledger.get_hash(key)
        
        try:
            data = self.operator.read(key, **options)
        except opendal.exceptions.NotFound:
            if expected_hash is not None:
                raise DataNotFoundException(key)
            raise
        
        if expected_hash is None:
            raise MissingAnchorException(key)
        
        current_hash = self._compute_hash(data)
        if expected_hash != current_hash:
            raise TamperDetectedException(key)

        return data
    
    def delete(self, key: str) -> None:
        key = self._normalize_path(key)
        self.operator.delete(key)
        self.ledger.delete(key)

    def copy(self, source: str, dest: str) -> None:
        source = self._normalize_path(source)
        dest = self._normalize_path(dest)
        data = self.read(source)
        self.operator.copy(source, dest)
        hash_value = self._compute_hash(data)
        self.ledger.store_hash(dest, hash_value)

    def rename(self, source: str, dest: str) -> None:
        source = self._normalize_path(source)
        dest = self._normalize_path(dest)
        data = self.read(source)
        self.operator.rename(source, dest)
        hash_value = self._compute_hash(data)
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
    
    @staticmethod
    def _compute_hash(data: bytes) -> bytes:
        return sha256(data).digest()

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
    