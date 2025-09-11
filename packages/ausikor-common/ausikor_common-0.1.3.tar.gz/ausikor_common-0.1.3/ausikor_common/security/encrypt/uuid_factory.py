import string
import shortuuid


class CreateUUID:
    def __init__(self, length: int, alphabet: str = string.ascii_lowercase + string.digits):
        self.length = length
        self.alphabet = alphabet

    def generate(self) -> str:
        return shortuuid.ShortUUID(alphabet=self.alphabet).random(length=self.length)


class UUIDFactory:
    def create(self, length: int, alphabet: str = string.ascii_lowercase + string.digits) -> CreateUUID:
        return CreateUUID(length, alphabet)