from yadisk import YaDisk
from yadisk.exceptions import YaDiskError


class YandexDisk:
    def __init__(self, token):
        self.token = token
        self.yadisk = YaDisk(token=token)

    async def valid(self):
        try:
            return self.yadisk.check_token()
        except YaDiskError as e:
            print(f"error - {e}")
            return False
