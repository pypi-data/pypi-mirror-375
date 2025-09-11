class PesapalException(Exception):
    def __init__(self, *, typ: str, code: str, message: str):
        super().__init__()
        self.type = typ
        self.code = code
        self.message = message

    def __str__(self):
        return f"({self.type} - {self.code}): {self.message}"
