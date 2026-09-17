---
name: email-presign
description: 이메일 사전등록/행사 발송 템플릿 제작 및 Cloudflare Pages 배포 자동화 스킬 (원본 이미지만으로 1000px 메인 및 카카오 소셜 이미지 자동 생성, 최신 HTML 기반 파생, 단일/복수 버튼 좌표 매핑, 클라우드 Git Push 및 배포)
---

# 이메일 사전등록 템플릿 자동화 스킬 (email-presign)

이 스킬은 행사/세미나/심포지엄 등의 **사전등록 이메일 발송 HTML 템플릿**을 제작할 때 필요한 전체 파이프라인(원본 이미지 분석, 1000px 메인 이미지 리사이징, 헤더 크롭 기반 소셜 이미지 자동 생성, 최신 템플릿 기반 HTML 파생, 단일/다중 버튼 이미지맵 좌표 매핑, Cloudflare Pages 배포)을 자동화합니다.

---

## 1. 핵심 입력 및 파일명 규칙 (File Naming Conventions)

사용자는 **원본 이미지 파일(예: `260917_joint.png`)**과 **이동할 타겟 URL(들)**만 입력으로 제공합니다.  
에이전트는 원본 이미지 파일명(`{YYMMDD}_{name}.ext`)을 감지하여 다음과 같이 일관된 네이밍 규칙으로 파일들을 자동 파생합니다:

| 구분 | 파일명 형식 | 설명 |
| :--- | :--- | :--- |
| **원본 이미지 (Input)** | `{YYMMDD}_{name}.png` | 사용자가 전달한 원본 행사 시안 이미지 (예: `260917_joint.png`) |
| **메인 리사이즈 이미지** | `email_{YYMMDD}_{name}_main.png` | 가로 1000px 비율 유지 고화질 리사이즈 이미지 |
| **소셜 공유 (`og:image`)** | `email_{YYMMDD}_{name}_kakao.png` | 상단 헤더 배너 크롭 기반 SNS 공유용 이미지 (약 1200x600) |
| **결과 HTML 파일** | `email_{YYMMDD}_{name}.html` | 최신 HTML 샘플을 상속받아 생성된 최종 템플릿 |

---

## 2. 5단계 자동화 파이프라인 (5-Step Pipeline)

### Step 0: 최신 HTML 템플릿 탐색 및 파라미터 확인
1. **기준 HTML 자동 탐색:** 프로젝트 내 존재하는 `email_*.html` 파일 중 **가장 최근에 작업/수정된 최신 HTML 파일**을 찾아 기본 구조(메타태그, 스타일, 맵 구조 등)의 베이스로 삼습니다.
2. **행사 정보 및 타겟 URL 확인:** 사용자 질의 또는 프롬프트로부터 버튼별 링크(예: 사전등록 URL, 초록접수 `Abstract Submission` URL 등)를 확인합니다.

---

### Step 1: 메인 1000px 리사이징 & 소셜 공유 이미지 자동 생성
파이썬 가상환경(`C:\Python37\python.exe`)의 PIL 라이브러리를 활용하여 2종의 이미지를 자동 생성합니다:
1. **메인 이미지 리사이징 (`email_{YYMMDD}_{name}_main.png`):**
   - 원본 가로폭을 이메일 표준 규격인 **가로 1000px**로 비율(Aspect Ratio) 유지 하에 리사이징 (`Image.Resampling.LANCZOS`).
2. **소셜 배너 크롭 (`email_{YYMMDD}_{name}_kakao.png`):**
   - 원본 이미지 상단의 메인 타이틀 배너(어두운 배경과 본문 흰색 배경 경계선 지점)를 자동 크롭한 후 SNS 공유 규격(가로 1200px)으로 최적화 저장.

---

### Step 2: 클라우드 (Cloudflare Pages) 호스팅 URL 확인
이메일 클라이언트는 상대 경로를 인식하지 못하므로, 생성된 이미지와 HTML 파일은 Cloudflare Pages 절대 경로로 연결됩니다.
* 호스팅 URL 양식: `https://hyo-email.pages.dev/[파일명]`
  - 메인 이미지: `https://hyo-email.pages.dev/email_{YYMMDD}_{name}_main.png`
  - 소셜 이미지: `https://hyo-email.pages.dev/email_{YYMMDD}_{name}_kakao.png`
  - HTML 페이지: `https://hyo-email.pages.dev/email_{YYMMDD}_{name}.html`

---

### Step 3: 최신 샘플 기반 HTML 템플릿 생성 & 단일/복수 버튼 좌표 매핑
1. **최신 HTML 베이스 복제 및 메타 정보 갱신:**
   - 최신 HTML 구조를 복사하여 `<title>`, `<meta property="og:title">`, `<meta property="og:image">`, `<img src="...">` 경로를 갱신합니다.
2. **단일/다중 버튼 이미지맵(`<area>`) 매핑:**
   - 시안 내 버튼이 1개(사전등록) 또는 2개 이상(초록접수 + 사전등록 등)인 경우를 지원합니다.
   - 각 버튼의 1000px 기준 `coords="x1,y1,x2,y2"`를 정밀하게 추출하여 `<map name="image-map">` 내에 `<area>` 태그로 등록합니다.
3. **하단 대체 텍스트 링크 다중 지원:**
   - 이미지 차단 수신자를 위해 하단 `이미지가 클릭되지 않나요?` 영역에 등록된 모든 버튼의 링크(예: `[사전등록 바로가기]`, `[Abstract Submission 바로가기]`)를 함께 제공합니다.

---

### Step 4 & 5: 좌표 검수 및 Git Push 자동 배포

#### A. 에이전트 자동 배포 (권장)
좌표 및 파일 생성이 완료되면 Windows 환경에 맞추어 원격 저장소에 원클릭 Push 배포합니다:
```bash
git add {YYMMDD}_{name}.png email_{YYMMDD}_{name}_main.png email_{YYMMDD}_{name}_kakao.png email_{YYMMDD}_{name}.html; git commit -m "Add email_{YYMMDD}_{name} template and images for Cloudflare Pages"; git push origin main
```

#### B. 웹 마우스 픽커 검수/수정 (선택 사항)
사용자가 직접 브라우저에서 드래그하여 좌표를 재설정하거나 가변 URL을 갱신하고자 할 경우:
1. **서버 실행:** `C:\Python37\python.exe server.py`
2. **브라우저 접속:** 👉 **[http://127.0.0.1:5000/picker](http://127.0.0.1:5000/picker)**
3. **영역 선택:** 마우스 드래그 시 붉은색(`#EF4444`, 반투명 빨강 박스)으로 표시되며, 하단 [🚀 좌표 적용 및 Cloudflare Pages 즉시 배포] 버튼 클릭 시 파일 갱신 및 Git Push가 자동 수행됩니다.
4. **로컬 다운로드 지원:** 배포 후 브라우저 및 `http://127.0.0.1:5000/api/download/<파일명>`을 통해 완성본 HTML 즉시 다운로드 가능.

---

## 3. 환경 및 실행 시 유의사항
- **파이썬 실행 환경:** `flask`, `Pillow` 등이 구비된 `C:\Python37\python.exe`를 사용합니다.
- **Windows 터미널 인코딩:** Windows 콘솔의 `cp949` 에러 방지를 위해 로그에는 이모지 대신 ASCII 태그(`[START]`, `[OK]`, `[URL]` 등)를 사용합니다.
- **명령어 연결자:** Windows PowerShell 환경에서는 `&&` 대신 세미콜론(`;`)을 사용합니다.
