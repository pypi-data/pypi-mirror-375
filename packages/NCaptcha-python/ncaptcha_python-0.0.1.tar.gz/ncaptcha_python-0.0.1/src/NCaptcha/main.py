from . import TextCaptcha, CaptchaOptions

def run_example():
    """
    캡챠 라이브러리의 사용 예시를 보여주는 함수.
    """
    print("----- 캡챠 라이브러리 예시 실행 -----")

    # 캡챠 객체 생성 (길이: 6, 캡챠 방식: 영어 대소문자, 유효시간: 30초)
    captcha = TextCaptcha(length=6, characters=CaptchaOptions.ENGLISH_ALL, expires_in_seconds=30)

    # 캡챠 문자열 생성
    captcha_text = captcha.generate()
    print(f"\n생성된 캡챠: {captcha_text}")
    print(f"만료 시간: {captcha.expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 사용자 입력 받기
    user_input = input("캡챠를 입력하세요: ")

    result = captcha.validate(user_input)

    # 입력 검증
    if result == "SUCCESS":
        print("\n성공! 캡챠 입력이 일치합니다.")
    elif result == "MISMATCH":
        print("\n실패! 유효시간이 만료되었습니다.")
    elif result == "EXPIRED":
        print("\n실패! 캡챠 입력이 일치하지 않습니다.")

    print("\n----- 예시 종료 -----")


if __name__ == "__main__":
    run_example()