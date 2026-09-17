# HYO Email Project Agent Rules (Antigravity & Codex)

이 저장소(`hyo_email`)에서 작업하는 모든 AI 에이전트(Antigravity, Codex 등)는 다음 규칙과 파이프라인을 준수해야 합니다.

## 1. 이메일 사전등록 자동화 파이프라인 (`email-presign`)
사전등록/행사 메일 발송 템플릿 관련 작업이나 `/email-presign` 요청 시 본 프로젝트에 내장된 `.agents/skills/email-presign/SKILL.md` 스킬 지침을 따릅니다.

### 핵심 5단계 파이프라인 요약
1. **입력 및 변수 자동 감지 (Step 0):**
   - 사용자가 원본 이미지(`{YYMMDD}_{name}.png`)와 타겟 URL만 제공하면, 기존 최신 `email_*.html` 샘플을 자동으로 찾아 기본 구조를 계승합니다.
   - 파생 파일명 규칙: 메인 `email_{YYMMDD}_{name}_main.png`, 소셜 `email_{YYMMDD}_{name}_kakao.png`, 결과 `email_{YYMMDD}_{name}.html`
2. **이미지 1000px 리사이징 & 소셜 이미지 자동 생성 (Step 1):**
   - 원본 가로 비율을 유지하여 가로 1000px 고화질(`PIL.Image.Resampling.LANCZOS`)로 메인 이미지를 리사이징합니다.
   - 상단 헤더 배너 비주얼 영역을 자동 크롭하여 카카오/SNS 공유용 이미지(`1200 x 600` 비율)를 자동 생성합니다.
3. **클라우드 절대 경로 매핑 (Step 2 & 3):**
   - Cloudflare Pages 호스팅 주소(`https://hyo-email.pages.dev/[파일명]`)를 기준으로 HTML 내 `<img src>`, `<meta property="og:image">`를 구성합니다.
4. **단일/다중 버튼 이미지맵 좌표 정밀 매핑 (Step 3):**
   - 사전등록뿐 아니라 초록접수(`Abstract Submission`) 등 2개 이상의 버튼이 있는 경우 각각의 `<area>` 좌표와 하단 대체 텍스트 링크를 유연하게 모두 생성합니다.
5. **원격 배포 및 웹 픽커 지원 (Step 4 & 5):**
   - Git Commit & Push로 Cloudflare Pages에 즉시 배포합니다.
   - 세부 수동 검수가 필요한 경우 로컬 웹 좌표 픽커(`http://127.0.0.1:5000/picker`)를 통해 붉은색 미리보기와 가변 URL 수정 및 로컬 다운로드를 지원합니다.

## 2. 서버 및 실행 환경 유의사항
- **파이썬 실행 경로:** 시스템 기본 `python` 대신 `flask`, `flask-cors`, `Pillow`가 구비된 `C:\Python37\python.exe`를 사용하여 실행합니다.
  ```bash
  C:\Python37\python.exe server.py
  ```
- **Windows 터미널 인코딩:** Windows `cmd` 콘솔의 `cp949` 인코딩 충돌을 방지하기 위해 `print()` 출력문에는 이모지 대신 ASCII 문자(`[START]`, `[OK]`, `[URL]` 등)를 사용합니다.
- **PowerShell 명령어:** 여러 명령어를 연결하여 실행할 때는 `&&` 대신 세미콜론(`;`)을 사용합니다.
- **최종 완성본 다운로드 제공:** 배포 완료 후 사용자에게 최종 HTML 파일 다운로드 URL(`http://127.0.0.1:5000/api/download/<파일명>`) 및 Cloudflare Pages 실시간 주소를 함께 제공합니다.
