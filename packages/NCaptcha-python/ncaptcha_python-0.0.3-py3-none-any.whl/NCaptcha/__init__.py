import random
import string
import datetime
import io
import uuid  # 고유 식별자 생성을 위해 추가
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -- 이미지 캡챠 관리 --
active_img_captchas = {}

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

    def __init__(self, length: int = 6, characters: str = CaptchaOptions.ENGLISH_ALL, expires_in_seconds: int = 30):
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
            raise ValueError("Length must be an integer greater than or equal to 1.")

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
            return CaptchaResult.EXPIRED

        if user_input == self.text:
            return CaptchaResult.SUCCESS
        else:
            return CaptchaResult.MISMATCH

# -- 이미지 --
class ImageCaptcha:
    """이미지 캡챠 생성 및 검증을 위한 클래스."""

    def __init__(self, length: int = 6, characters: str = CaptchaOptions.DIGITS_ENGLISH_ALL,
                 size: tuple[int, int] = (200, 80), font: str = "arial.ttf", font_size: int = 40,
                 noise_level: int = 200, expires_in_seconds: int = 30):
        """
        이미지 캡챠 객체를 초기화합니다.

        :param length: 캡챠 문자열의 길이
        :param characters: 캡챠에 사용할 문자 풀
        :param size: 이미지 크기 (너비, 높이)
        :param font: 폰트
        :param font_size: 폰트 크기
        :param noise_level: 노이즈의 강도 (점을 찍는 횟수)
        :param expires_in_seconds: 캡챠의 유효 시간 (초 단위)
        """
        self.length = length
        self.characters = characters
        self.size = size
        self.font = font
        self.font_size = font_size
        self.noise_level = noise_level
        self.expires_in_seconds = expires_in_seconds

        self.text = ""
        self.expiration_time = None
        self._image_buffer = None  # 메모리 버퍼를 저장할 내부 변수

    def generate(self) -> tuple[str, io.BytesIO, str]:
        """
        캡챠 이미지와 정답 문자열을 생성하고 반환합니다.

        :return: 이미지 데이터를 담은 메모리 버퍼와 정답 문자열
        """
        if not isinstance(self.length, int) or self.length <= 0:
            raise ValueError("Length must be an integer greater than or equal to 1.")

        # 캡챠 문자열 생성 및 유효시간 설정
        self.text = ''.join(random.choice(self.characters) for _ in range(self.length))
        self.expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=self.expires_in_seconds)

        # 캡챠 이미지 생성
        image = Image.new('RGB', self.size, 'white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(self.font, self.font_size)
        except IOError:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), self.text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # 텍스트 그리기 (위치 조정)
        x = (self.size[0] - text_width) / 2
        y = (self.size[1] - text_height) / 2
        draw.text((x, y), self.text, font=font, fill="black")

        # 노이즈 추가 (노이즈 강도 매개변수 사용)
        for _ in range(self.noise_level):
            draw.point((random.randint(0, self.size[0]), random.randint(0, self.size[1])), fill=(0, 0, 0))

        # 이미지를 메모리 버퍼에 저장하고 객체에 할당
        self._image_buffer = io.BytesIO()
        image.save(self._image_buffer, 'PNG')
        self._image_buffer.seek(0)

        captcha_id = str(uuid.uuid4())  # 고유한 ID 생성

        active_img_captchas[captcha_id] = self

        return captcha_id, self.get_image_buffer(), self.text

    def get_image_buffer(self) -> io.BytesIO:
        """현재 캡챠 객체에 저장된 메모리 버퍼를 반환합니다."""
        if self._image_buffer:
            self._image_buffer.seek(0)
        return self._image_buffer

    def clear_data(self):
        """캡챠 데이터를 초기화하여 메모리에서 삭제합니다."""
        self.text = ""
        self.expiration_time = None
        if self._image_buffer:
            self._image_buffer.close()
            self._image_buffer = None

    def validate(self, user_input: str) -> str:
        """
        사용자 입력과 캡챠의 유효성을 검증하고 결과를 문자열로 반환합니다.
        유효성 검증 후에는 데이터를 초기화합니다.

        :param user_input: 사용자가 입력한 문자열
        :return: 유효성 검증 결과 (SUCCESS, EXPIRED, MISMATCH)
        """
        # 데이터가 이미 삭제된 경우
        if not self.text:
            return CaptchaResult.MISMATCH

        # 만료 시간 확인
        if datetime.datetime.now() > self.expiration_time:
            self.clear_data()
            return CaptchaResult.EXPIRED

        # 입력 값과 정답 비교 후 데이터 삭제
        if user_input == self.text:
            self.clear_data()
            return CaptchaResult.SUCCESS
        else:
            self.clear_data()
            return CaptchaResult.MISMATCH


def image_validate(captcha_id: str, user_input: str) -> str:
    # 캡챠 ID를 사용하여 중앙 저장소에서 기존 캡챠 객체를 가져옵니다.
    # 만약 ID가 존재하지 않으면, 이미 만료되었거나 잘못된 ID입니다.
    if captcha_id not in active_img_captchas:
        return CaptchaResult.EXPIRED

    captcha_obj = active_img_captchas[captcha_id]

    # 만료 시간 확인
    if datetime.datetime.now() > captcha_obj.expiration_time:
        # 만료된 캡챠는 저장소에서 제거합니다.
        del active_img_captchas[captcha_id]
        return CaptchaResult.EXPIRED

    # 입력 값과 정답 비교
    if user_input == captcha_obj.text:
        # 성공했으니 저장소에서 제거합니다.
        del active_img_captchas[captcha_id]
        return CaptchaResult.SUCCESS
    else:
        # 실패했으니 저장소에서 제거합니다.
        del active_img_captchas[captcha_id]
        return CaptchaResult.MISMATCH

def remove_captcha(captcha_id: str) -> bool:
    """
    캡챠를 저장소에서 제거합니다.

    :param captcha_id: 캡챠의 고유 ID
    :return: 결과 bool
    """
    if captcha_id not in active_img_captchas:
        return False  # ID가 없으면 이미 만료되거나 사용된 것

    # 저장소에서 제거
    del active_img_captchas[captcha_id]

    return True


def cleanup_expired_captchas():
    """
    모든 캡챠를 순회하며 유효기간이 지난 캡챠를 제거합니다.
    이 함수는 백그라운드 스레드나 스케줄러로 주기적으로 실행되어야 합니다.
    """
    now = datetime.datetime.now()
    expired_ids = []

    for captcha_id, captcha_obj in active_img_captchas.items():
        if captcha_obj.expiration_time < now:
            expired_ids.append(captcha_id)

    for captcha_id in expired_ids:
        print(f"만료된 캡챠 ID '{captcha_id}' 제거.")
        del active_img_captchas[captcha_id]