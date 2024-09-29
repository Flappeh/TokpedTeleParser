from telegram.error import BadRequest

from peewee import DatabaseError
class InvalidWalletKeyError(BadRequest):
    def __init__(self, message: str):
        super().__init__(message)
        
class PiAccountError(DatabaseError):
    def __init__(self, *args, message) -> None:
        super().__init__(*args, message)