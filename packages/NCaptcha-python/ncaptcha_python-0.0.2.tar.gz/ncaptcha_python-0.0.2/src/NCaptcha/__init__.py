import random
import string
import datetime


# 이전 답변의 CaptchaOptions 클래스를 그대로 사용합니다.
class CaptchaOptions:
    ENGLISH_LOWER = string.ascii_lowercase
    ENGLISH_UPPER = string.ascii_uppercase
    ENGLISH_ALL = string.ascii_letters

    DIGITS = string.digits
    DIGITS_ENGLISH_LOWER = string.digits + string.ascii_lowercase
    DIGITS_ENGLISH_UPPER = string.digits + string.ascii_uppercase
    DIGITS_ENGLISH_ALL = string.digits + string.ascii_letters

    SYMBOLS = string.punctuation
    SYMBOLS_ENGLISH_LOWER = string.punctuation + string.ascii_lowercase
    SYMBOLS_ENGLISH_UPPER = string.punctuation + string.ascii_uppercase
    SYMBOLS_ENGLISH_ALL = string.punctuation + string.ascii_letters
    SYMBOLS_DIGITS = string.punctuation + string.digits
    SYMBOLS_ENGLISH_LOWER_DIGITS = string.punctuation + string.ascii_lowercase + string.digits
    SYMBOLS_ENGLISH_UPPER_DIGITS = string.punctuation + string.ascii_uppercase + string.digits
    SYMBOLS_ENGLISH_ALL_DIGITS = string.punctuation + string.ascii_letters + string.digits

class CaptchaResult:
    SUCCESS = "SUCCESS"
    MISMATCH = "MISMATCH"
    EXPIRED = "EXPIRED"


class TextCaptcha:
    """캡챠 생성 및 검증을 위한 클래스."""

    def __init__(self, length: int = 6, characters: str = CaptchaOptions.ENGLISH_ALL, expires_in_seconds: int = 300):
        """
        캡챠 객체를 초기화합니다.

        :param length: 캡챠 문자열의 길이
        :param characters: 캡챠에 사용할 문자 풀
        :param expires_in_seconds: 캡챠의 유효 시간 (초 단위)
        """
        self.length = length
        self.characters = characters
        self.expires_in_seconds = expires_in_seconds
        self.text = ""
        self.expiration_time = None

    def generate(self) -> str:
        """
        캡챠 문자열을 생성하고 유효시간을 설정합니다.

        :return: 생성된 캡챠 문자열
        """
        if not isinstance(self.length, int) or self.length <= 0:
            raise ValueError("길이(length)는 1 이상의 정수여야 합니다.")

        self.text = ''.join(random.choice(self.characters) for _ in range(self.length))
        self.expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_in_seconds)
        return self.text

    def validate(self, user_input: str) -> str:
        """
        사용자 입력과 캡챠의 유효성을 검증하고 결과를 문자열로 반환합니다.

        :param user_input: 사용자가 입력한 문자열
        :return: 유효성 검증 결과 (SUCCESS, EXPIRED, MISMATCH)
        """
        if datetime.datetime.now() > self.expiration_time:
            print("[Captcha] 유효시간이 만료되었습니다.")
            return CaptchaResult.EXPIRED

        if user_input == self.text:
            print("[Captcha] 입력이 일치합니다.")
            return CaptchaResult.SUCCESS
        else:
            print("[Captcha] 입력이 올바르지 않습니다.")
            return CaptchaResult.MISMATCH