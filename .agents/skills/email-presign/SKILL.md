---
name: email-presign
description: 이메일 사전등록 발송 템플릿 제작 및 Cloudflare Pages 배포 자동화 스킬 (이미지 1000px 리사이징, 클라우드 Git Push, 절대 URL 주소 링크 수정, 웹 마우스 좌표 드래그 설정 및 배포 지원)
---

# 이메일 사전등록 템플릿 자동화 스킬 (email-presign)

이 스킬은 행사/세미나 등의 **사전등록 이메일 발송 HTML 템플릿**을 제작할 때 필요한 전체 파이프라인(이미지 리사이징, 클라우드 배포, 절대 경로 수정, 마우스 드래그 기반 이미지맵 좌표 픽킹, 타겟 URL 가변 적용 및 최종 배포)을 자동화합니다.

---

## 1. 동작 프로세스 (5-Step Pipeline)

### Step 0: 사용자 질의 및 변수 확인 (Variables)
메인 이미지나 소셜 공유(`og:image`) 이미지, 이동 URL은 행사마다 변경될 수 있으므로, 에이전트는 스킬 시작 시 다음 파라미터를 사용자에게 확인(질의)하거나 명확한 기본값을 적용합니다.
* **메인 시안 이미지 파일:** 예: `email_260519_baby_main.png`
* **소셜 공유(`og:image`) 이미지 파일:** 예: `email_260519_kakao.png`
* **기준 HTML 템플릿 파일:** 예: `email_260519_baby.html`
* **버튼 클릭 시 이동할 타겟 URL (`href`):** 예: `https://www.neonatology.or.kr/conference/seminar2/info.html` (Step 4, 5 웹 픽커 화면에서도 자유롭게 가변 변경 가능)

---

### Step 1: 메인 시안 이미지 1000px 리사이징
이메일 클라이언트 로딩 속도 최적화 및 템플릿 가로 규격(1000px) 일치를 위해, 원본 메인 이미지를 비율(Aspect Ratio) 유지 하에 **가로 1000px**로 리사이징합니다.
* 파이썬 PIL 라이브러리를 활용하여 `Image.Resampling.LANCZOS` 고화질 리사이징을 수행합니다.

---

### Step 2: 클라우드(Cloudflare Pages) Push 및 호스팅 URL 확인
이메일 클라이언트는 상대 경로(`<img src="main.png">`)를 지원하지 않으므로, 리사이징된 메인 이미지 및 소셜 공유 이미지를 먼저 GitHub(`origin/main`)에 Push하여 Cloudflare Pages를 통해 외부 호스팅 절대 URL을 생성합니다.
* 실행 커맨드:
  ```bash
  git add [메인_이미지] [소셜_이미지]
  git commit -m "Upload email template images to Cloudflare Pages"
  git push origin main
  ```
* 호스팅 URL 양식: `https://hyo-email.pages.dev/[파일명]`

---

### Step 3: HTML 템플릿 내 이미지 경로 및 소셜 메타태그 수정
HTML 파일 내 이미지 소스와 메타 태그를 Step 2에서 배포된 Cloudflare Pages 절대 경로 URL로 수정합니다.
1. 메인 시안 이미지 URL: `<img src="https://hyo-email.pages.dev/email_260519_baby_main.png" width="1000" usemap="#image-map" ...>`
2. 소셜 공유 메타 이미지 URL: `<meta property="og:image" content="https://hyo-email.pages.dev/email_260519_kakao.png" />`

---

### Step 4 & 5: 웹 기반 마우스 드래그 Map 좌표 픽커, 가변 Target URL 입력 및 자동 배포 (Web Interactive Picker)
사용자가 직접 픽셀 좌표를 계산할 필요 없이, 브라우저 상에서 **마우스 드래그**로 손쉽게 좌표를 설정하고 한 번에 Cloudflare Pages로 배포할 수 있는 웹 픽커를 제공합니다.

1. **로컬 API 서버 실행:**
   ```bash
   C:\Python37\python.exe server.py
   ```
2. **브라우저 접속 주소 안내:**
   👉 **[http://127.0.0.1:5000/picker](http://127.0.0.1:5000/picker)**
3. **웹 픽커 이용 및 배포 방법:**
   - **(가변 URL 설정):** 상단 제어바의 `🔗 사전 가입버튼 이동 URL (Target Link)` 입력창에 원하는 사전등록 가입 페이지 주소(`href`)를 자유롭게 입력합니다.
   - **(마우스 드래그 선택):** 이미지 위에서 마우스를 클릭한 채 드래그하여 버튼 좌표 영역(`<area>`)을 그립니다. 이때 드래그 영역은 **붉은색(`#EF4444`, 반투명 빨강)**으로 표시되며 실제 HTML 파일 수정 없이 눈으로 확인하는 용도로만 표시됩니다.
   - **(최종 반영 및 배포):** 하단의 **[🚀 좌표 적용 및 Cloudflare Pages 즉시 배포]** 버튼을 누르면, 서버가 자동으로 HTML 파일 내 `<map>` 태그 좌표와 하단 대체 링크(`<a href="...">[사전등록 바로가기]</a>`)를 지정한 Target URL로 갱신하고 `git push origin main`을 실행하여 최종 완성본 배포를 마칩니다.
   - **(최종 완성본 다운로드):** 배포 성공 시 하단 성공 창에 생성되는 **[💾 최종 HTML 파일 내 컴퓨터로 다운로드]** 버튼을 통해 완성본을 즉시 다운로드할 수 있습니다.
