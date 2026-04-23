class TamperException(Exception):
    def __init__(self, input):
        self.input = input

class TamperDetectedException(TamperException):
    def __str__(self):
        return f"Tampering detected in {self.input}! Hash mismatch."

class MissingAnchorException(TamperException):
    def __str__(self):
        return f"Tampering detected in {self.input}! Missing anchor."

class DataNotFoundException(TamperException):
    def __str__(self):
        return f"Tampering detected in {self.input}! Missing data."
    
class BulkTamperException(TamperException):
    def __init__(self, violations: dict[str, TamperException], results: dict[str, bytes]):
        self.violations = violations  # key -> exception
        self.results = results        # key -> data (for records that passed)

    def __str__(self):
        lines = [f"Tampering detected in {len(self.violations)} record(s):"]
        for key, exc in self.violations.items():
            lines.append(f"  {key}: {exc}")
        return "\n".join(lines)