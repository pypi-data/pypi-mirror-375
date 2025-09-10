from . import TextCaptcha, ImageCaptcha, CaptchaOptions, CaptchaResult
from . import remove_captcha, cleanup_expired_captchas, image_validate
from flask import Flask, send_file, request

app = Flask(__name__)

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
    if result == CaptchaResult.SUCCESS:
        print("\n성공! 캡챠 입력이 일치합니다.")
    elif result == CaptchaResult.EXPIRED:
        print("\n실패! 유효시간이 만료되었습니다.")
    elif result == CaptchaResult.MISMATCH:
        print("\n실패! 캡챠 입력이 일치하지 않습니다.")

    print("\n----- 예시 종료 -----")


def run_image_example():
    """
    이미지 캡챠 라이브러리의 사용 예시를 보여주는 함수.
    """
    print("----- 이미지 캡챠 예시 실행 -----")

    app.run(debug=True)

    cleanup_expired_captchas()

    print("\n----- 예시 종료 -----")

@app.route("/captcha.png")
def serve_captcha():
    """새로운 캡챠 이미지를 반환하는 엔드포인트."""
    try:
        # 캡챠 객체 생성
        captcha = ImageCaptcha(length=4, characters=CaptchaOptions.ENGLISH_LOWER, font_size=20, expires_in_seconds=30)

        captcha_id, captcha_buffet, captcha_text = captcha.generate()

        # 이미지 데이터를 HTTP 응답으로 반환
        response = send_file(captcha_buffet, mimetype='image/png')
        response.headers['X-Captcha-ID'] = captcha_id
        response.headers['X-Captcha-TEXT'] = captcha_text

        return response
    except Exception as e:
        print(f"캡챠 생성 오류: {e}")
        return "Internal Server Error", 500

@app.route("/validate_captcha", methods=["POST"])
def validate_captcha():
    """사용자 입력 값을 검증하는 엔드포인트."""
    user_input = request.form.get("captcha_input")
    captcha_id = request.form.get("captcha_id")

    result = image_validate(captcha_id, user_input)

    if result == CaptchaResult.SUCCESS:
        message = "✅ 캡챠 입력이 일치합니다!"
        color = "green"
    elif result == CaptchaResult.MISMATCH:
        message = "❌ 캡챠 입력이 올바르지 않습니다."
        color = "red"
    else: # CaptchaResult.EXPIRED
        message = "⚠️ 캡챠 유효시간이 만료되었거나 ID가 잘못되었습니다. 다시 시도해주세요."
        color = "orange"

    return f"""
    <div style="text-align:center;">
        <h2 style="color:{color};">{message}</h2>
        <a href="/">돌아가기</a>
    </div>
    """


@app.route("/")
def index():
    """캡챠 이미지와 입력 필드를 보여주는 HTML 페이지."""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>캡챠 예시</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
            }
            #captcha-container {
                border: 1px solid #ccc;
                padding: 20px;
                display: inline-block;
                border-radius: 8px;
            }
            #captcha-image {
                border: 1px solid #000;
                margin-bottom: 15px;
            }
            #captcha-input {
                padding: 8px;
                width: 200px;
                margin-right: 10px;
            }
            #submit-button {
                padding: 8px 15px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>캡챠 예시</h1>
        <div id="captcha-container">
            <img id="captcha-image" alt="CAPTCHA Image">
            <form action="/validate_captcha" method="post">
                <input type="text" name="captcha_input" id="captcha-input" placeholder="여기에 캡챠를 입력하세요">
                <input type="hidden" name="captcha_id" id="captcha-id">
                <button type="submit" id="submit-button">제출</button>
            </form>
        </div>
    </body>
    <script>
        window.onload = async function() {
            const captchaImage = document.getElementById('captcha-image');
            const captchaIdInput = document.getElementById('captcha-id');
    
            // URL 뒤에 타임스탬프를 추가하여 캐싱을 방지합니다.
            const imageUrl = '/captcha.png?t=' + Date.now();
    
            // fetch를 통해 캡챠 이미지와 ID를 한 번에 가져옵니다.
            const response = await fetch(imageUrl);
            const captchaId = response.headers.get('X-Captcha-ID');
            
            // 이미지 데이터를 ArrayBuffer로 변환합니다.
            const blob = await response.blob();
            
            // Blob을 Base64 문자열로 변환하여 img src에 직접 할당합니다.
            const reader = new FileReader();
            reader.onloadend = function() {
                captchaImage.src = reader.result;
            }
            reader.readAsDataURL(blob);
    
            captchaIdInput.value = captchaId;
        };
    </script>
    </html>
    """

if __name__ == "__main__":
    run_image_example()