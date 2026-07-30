import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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

@app.route('/picker')
def picker():
    html_path = os.path.join(BASE_DIR, 'Map_Coordinate_Picker.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    return "Map_Coordinate_Picker.html 파일이 존재하지 않습니다.", 404

@app.route('/api/files', methods=['GET'])
def list_files():
    images = []
    htmls = []
    for f in os.listdir(BASE_DIR):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(f)
        elif f.lower().endswith('.html') and f not in ['Email_Template_Builder.html', 'Map_Coordinate_Picker.html', 'test.html']:
            htmls.append(f)
    return jsonify({"images": sorted(images), "html_files": sorted(htmls)})

@app.route('/api/save_map', methods=['POST'])
def save_map():
    try:
        data = request.json
        html_file = data.get('html_file')
        areas = data.get('areas', [])
        do_push = data.get('push', True)
        target_url = data.get('target_url')

        if not html_file or not os.path.exists(os.path.join(BASE_DIR, html_file)):
            return jsonify({"success": False, "error": "HTML 파일이 지정되지 않았거나 존재하지 않습니다."}), 400

        html_path = os.path.join(BASE_DIR, html_file)
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Build area tags
        area_html_lines = []
        for area in areas:
            coords = area.get('coords', '')
            href = area.get('href') or target_url or 'https://www.neonatology.or.kr/conference/seminar2/info.html'
            alt = area.get('alt', '사전등록 바로가기')
            title = area.get('title', '사전등록 바로가기')
            area_html_lines.append(f'            <area target="_blank" alt="{alt}" title="{title}"\n                href="{href}"\n                coords="{coords}" shape="rect">')
        
        new_areas_block = "\n".join(area_html_lines)

        # Replace <map ...> ... </map> contents
        import re
        pattern = re.compile(r'(<map\s+name=["\']image-map["\']>)(.*?)(</map>)', re.DOTALL | re.IGNORECASE)
        if not pattern.search(content):
            return jsonify({"success": False, "error": "<map name=\"image-map\"> 태그를 HTML 내에서 찾을 수 없습니다."}), 400

        updated_content = pattern.sub(r'\1\n' + new_areas_block + r'\n        \3', content)

        # Update fallback <a> links in HTML if target_url is specified or from first area
        effective_url = target_url or (areas[0].get('href') if areas else None)
        if effective_url:
            fallback_pattern = re.compile(r'(<a\s+[^>]*?href=["\'])([^"\']*)(["\'][^>]*?>\s*\[?사전등록\s*바로가기\]?\s*</a>)', re.IGNORECASE)
            updated_content = fallback_pattern.sub(r'\g<1>' + effective_url + r'\g<3>', updated_content)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        if do_push:
            subprocess.run(["git", "add", html_file], check=True, cwd=BASE_DIR)
            commit_res = subprocess.run(["git", "commit", "-m", f"Auto-deploy map coordinates: {html_file}"], cwd=BASE_DIR, capture_output=True, text=True)
            print("Commit output:", commit_res.stdout)
            push_res = subprocess.run(["git", "push"], check=True, cwd=BASE_DIR, capture_output=True, text=True)
            print("Push output:", push_res.stdout)

        return jsonify({
            "success": True,
            "url": f"https://hyo-email.pages.dev/{html_file}",
            "download_url": f"/api/download/{html_file}",
            "message": f"{html_file} 좌표 설정 및 Cloudflare Pages 배포가 완료되었습니다!"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/<filename>')
def serve_static(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return "File not found", 404

if __name__ == '__main__':
    print("========================================")
    print("[START] 이메일 템플릿 로컬 서버 시작")
    print("[URL] 템플릿 빌더: http://127.0.0.1:5000")
    print("[URL] 마우스 좌표 픽커: http://127.0.0.1:5000/picker")
    print("========================================")
    app.run(host='127.0.0.1', port=5000, debug=True)

