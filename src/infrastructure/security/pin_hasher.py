import bcrypt


class PinHasher:
    @staticmethod
    def hash(pin: str) -> str:
        return bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify(pin: str, pin_hash: str) -> bool:
        try:
            return bcrypt.checkpw(pin.encode("utf-8"), pin_hash.encode("utf-8"))
        except ValueError:
            return False
