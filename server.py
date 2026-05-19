from flask import Flask, request, jsonify, send_file
import os
import subprocess
import base64

app = Flask(__name__)
# 현재 파일이 위치한 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__name__))

@app.route('/')
def index():
    # 루트 접속 시 Email_Template_Builder.html 서빙
    html_path = os.path.join(BASE_DIR, 'Email_Template_Builder.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    return "Email_Template_Builder.html 파일이 존재하지 않습니다.", 404

@app.route('/api/push', methods=['POST'])
def push_to_git():
    try:
        data = request.json
        filename = data.get('filename')
        html_content = data.get('html')
        image_base64 = data.get('image_base64')

        if not filename or not html_content or not image_base64:
            return jsonify({"success": False, "error": "필수 데이터가 누락되었습니다."}), 400

        # 이미지 저장
        img_path = os.path.join(BASE_DIR, f"{filename}.jpg")
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # HTML 저장
        html_path = os.path.join(BASE_DIR, f"{filename}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Git 커맨드 실행 (add -> commit -> push)
        subprocess.run(["git", "add", f"{filename}.jpg", f"{filename}.html"], check=True, cwd=BASE_DIR)
        
        # 커밋 (변경된 사항이 없으면 오류가 날 수 있으므로 예외 처리)
        commit_res = subprocess.run(["git", "commit", "-m", f"Auto-deploy: {filename}"], cwd=BASE_DIR, capture_output=True, text=True)
        print("Commit output:", commit_res.stdout)
        
        # 푸시
        push_res = subprocess.run(["git", "push"], check=True, cwd=BASE_DIR, capture_output=True, text=True)
        print("Push output:", push_res.stdout)

        return jsonify({"success": True})

    except subprocess.CalledProcessError as e:
        error_msg = f"Git 명령어 실행 실패:\n{e.stderr if e.stderr else str(e)}"
        print(error_msg)
        return jsonify({"success": False, "error": error_msg}), 500
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("========================================")
    print("🚀 이메일 템플릿 로컬 서버 시작")
    print("👉 브라우저를 열고 http://127.0.0.1:5000 에 접속하세요!")
    print("========================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
