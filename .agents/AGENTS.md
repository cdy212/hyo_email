# HYO Email Project Agent Rules (Antigravity & Codex)

이 저장소(`hyo_email`)에서 작업하는 모든 AI 에이전트(Antigravity, Codex 등)는 다음 규칙과 파이프라인을 준수해야 합니다.

## 1. 이메일 사전등록 자동화 파이프라인 (`email-presign`)
사전등록 메일 발송 템플릿 관련 작업이나 `/email-presign` 요청 시 본 프로젝트에 내장된 `.agents/skills/email-presign/SKILL.md` 스킬 지침을 따릅니다.

### 핵심 5단계 (5-Step Pipeline)
1. **Step 0**: 메인 이미지, 소셜 이미지, 대상 HTML, 타겟 이동 URL 변수 확인
2. **Step 1**: 메인 시안 이미지 비율 유지 가로 1000px 고화질 리사이징 (`PIL`)
3. **Step 2**: Cloudflare Pages 호스팅을 위해 Git Push 및 절대 경로 URL (`https://hyo-email.pages.dev/...`) 확인
4. **Step 3**: HTML 파일 내 `<img src>` 및 `<meta property="og:image">` 경로를 절대 주소로 갱신
5. **Step 4 & 5**: 로컬 웹 좌표 픽커(`http://127.0.0.1:5000/picker`)를 통한 좌표 설정, 가변 URL 입력, 붉은색 선택 미리보기 확인 및 원클릭 Push 배포

## 2. 서버 및 실행 환경 유의사항
- **파이썬 실행 경로:** 시스템 내장 기본 `python` 대신 필요한 의존성(`flask`, `flask-cors`, `Pillow`)이 설치된 `C:\Python37\python.exe`를 사용하여 실행합니다.
  ```bash
  C:\Python37\python.exe server.py
  ```
- **Windows 터미널 인코딩:** Windows `cmd` 콘솔의 `cp949` 인코딩 충돌을 방지하기 위해 `print()` 출력문에는 이모지 대신 ASCII 문자(`[START]`, `[OK]`, `[URL]` 등)를 사용합니다.
- **최종 완성본 다운로드 제공:** 배포 완료 후 사용자에게 최종 HTML 파일 다운로드 URL(`http://127.0.0.1:5000/api/download/<파일명>`) 및 Cloudflare Pages 실시간 주소를 함께 제공합니다.
