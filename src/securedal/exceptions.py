class TamperException(Exception):
    def __init__(self, input):
        self.input = input

class TamperDetectedException(TamperException):
    description = "Storage data hash and EIS anchor are different. Storage data may have been maliciously modified."
    def __str__(self):
        return f"Tampering detected in {self.input}! Hash mismatch.\n   {self.description}"

class MissingAnchorException(TamperException):
    description = "EIS anchor is missing while storage data and the mapping exists. Anchor may have been maliciously deleted or modified."
    def __str__(self):
        return f"Tampering detected in {self.input}! Missing expected anchor.\n   {self.description}"

class MissingDataException(TamperException):
    description = "Storage data is missing while its record in the mapping exists. Storage data may have been maliciously deleted."
    def __str__(self):
        return f"Tampering detected in {self.input}! Missing expected data.\n   {self.description}"
    
class UntrackedObjectException(TamperException):
    description = "Storage object exists but has no mapping. Object may have been added outside the integrity tracking system."
    def __str__(self):
        return f"Tampering detected in {self.input}! Object exists without integrity tracking.\n   {self.description}"
    
class OrphanMappingException(TamperException):
    description = "Mapping exists but both storage data and EIS anchor are missing. Both may have been maliciously deleted."
    def __str__(self):
        return f"Tampering detected in {self.input}! Orphan mapping (expected data and anchor missing).\n   {self.description}"
    
class BulkTamperException(TamperException):
    def __init__(self, violations: dict[str, TamperException], results: dict[str, bytes]):
        self.violations = violations  # key -> exception
        self.results = results        # key -> data (for records that passed)

    def __str__(self):
        lines = [f"Tampering detected in {len(self.violations)} record(s):"]
        for key, exc in self.violations.items():
            lines.append(f"  {key}: {exc}")
        return "\n".join(lines)