# NCaptcha-python
파이썬용 **NCaptcha** 입니다.  

***NCaptcha***는 간단한 캡챠를 구현한 라이브러리 입니다.  
몇줄 안되는 코드로 간단하게 구현할 수 있습니다.  
**간단한 라이브러리이기 때문에 보안이 중요한 곳에서는 사용하지 마세요.**

---

사용할 수 있는 캡챠는

- 영어(소) [ENGLISH_LOWER]
- 영어(대) [ENGLISH_UPPER]
- 영어(소, 대) [ENGLISH_ALL]
- 
- 숫자 [DIGITS]
- 숫자+영어(소) [DIGITS_ENGLISH_LOWER]
- 숫자+영어(대) [DIGITS_ENGLISH_UPPER]
- 숫자+영어(소, 대) [DIGITS_ENGLISH_ALL]
- 
- 특수문자 [SYMBOLS]
- 특수문자+영어(소) [SYMBOLS_ENGLISH_LOWER]
- 특수문자+영어(대) [SYMBOLS_ENGLISH_UPPER]
- 특수문자+영어(소, 대) [SYMBOLS_ENGLISH_ALL]
- 특수문자+숫자 [SYMBOLS_DIGITS]
- 특수문자+영어(소)+숫자 [SYMBOLS_ENGLISH_LOWER_DIGITS]
- 특수문자+영어(대)+숫자 [SYMBOLS_ENGLISH_UPPER_DIGITS]
- 특수문자+영어(소, 대)+숫자 [SYMBOLS_ENGLISH_ALL_DIGITS]

---

**설치**
```shell
pip install NCaptcha-python
```

---

# **사용방법**
```python
import NCaptcha

captcha = NCaptcha.TextCaptcha(length=6, characters=NCaptcha.CaptchaOptions.ENGLISH_ALL, expires_in_seconds=30)

# 캡챠 생성
captcha_text = captcha.generate()

print(f"\n생성된 캡챠: {captcha_text}")
print(f"만료 시간: {captcha.expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 사용자 입력 받기
user_input = input("캡챠를 입력하세요: ")

result = captcha.validate(user_input)

# 입력 검증
if result == NCaptcha.CaptchaResult.SUCCESS:
        ("\n성공! 캡챠 입력이 일치합니다.")
elif result == NCaptcha.CaptchaResult.EXPIRED:
    print("\n실패! 유효시간이 만료되었습니다.")
elif result == NCaptcha.CaptchaResult.MISMATCH:
    print("\n실패! 캡챠 입력이 일치하지 않습니다.")
```