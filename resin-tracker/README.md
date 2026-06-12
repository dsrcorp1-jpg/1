# PP/PE 레진 구매 관리 시스템

원재료(PP/PE 레진) 구매 전 과정을 한눈에 추적하는 대시보드입니다.  
단가 네고 → 계약 체결 → 선적 → 입항 → 통관 → 배차 완료까지 모든 단계를 관리합니다.

---

## 파일 구조

```
index.html          ← 대시보드 메인 (브라우저에서 바로 열기)
data/
  data.json         ← 전체 데이터 (오더·재고·시장가)
.claude/
  settings.json     ← 에이전트 팀 설정 + PostToolUse 훅 (data.json stage 자동 검증)
  agents/
    resin-data-validator.md  ← 데이터 검증 전용 에이전트 (읽기 전용)
    dashboard-dev.md         ← HTML/JS 개발 전담 에이전트
    doc-reviewer.md          ← 문서 품질 검토 에이전트 (읽기 전용)
  hooks/
    validate-stage.ps1       ← data.json 저장 시 stage 값 자동 차단 훅
skills/
  briefing-improver.md  ← 품질 개선 자동화 스킬 (issue-writer → issue-runner → doc-optimizer)
  issue-writer.md       ← 약점 발견 → GitHub 이슈 등록
  issue-runner.md       ← 이슈 → 코드 수정 → 이슈 종료
  doc-optimizer.md      ← 문서 검토 및 개선
  data-update.md        ← 오더·재고 데이터 입력 가이드 + 템플릿
README.md           ← 이 파일
```

---

## 실행 방법

`index.html`은 외부 JSON 파일을 읽기 때문에 **반드시 로컬 서버**로 실행해야 합니다.

### Python (권장)
```powershell
$py = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
cd C:\path\to\resin-tracker
& $py -m http.server 8080
```
→ 브라우저에서 `http://localhost:8080/index.html` 접속 (루트 `/`는 디렉토리 목록만 표시됨)

### VS Code
Live Server 확장 설치 후 `index.html` 우클릭 → **Open with Live Server**

---

## 탭별 기능

| 탭 | 기능 |
|----|------|
| 📊 **대시보드** | 전체 오더 요약, 긴급 알림, 오더별 단계 스테퍼 |
| 💬 **단가 네고** | 품목별 오퍼가·계약가·절감액 요약 + 오더별 상세 |
| 📝 **계약 관리** | 품목별 계약 현황 요약 + 계약 상세 내역 |
| 🚢 **선적·운송** | ETD 임박순 정렬, 14일 내 입항 예정 건 강조 |
| 🏛 **통관·배차** | 통관 + 배차 동시 현황, 진행중 건 강조 |
| 📦 **재고 현황** | 품목별 현재고·안전재고·입출고예정·재고일수(DOI) |
| 📈 **품목 이력** | 월별 시장가 추이 차트 + 오더 이력 전체 |

---

## 데이터 수정 방법

### 오더 추가/수정
`data/data.json` 파일의 `orders` 배열에 항목을 추가하거나 수정합니다.

**오더 단계값 (stage) — 아래 값만 사용 가능, 오타 주의:**
```
네고중 → 계약완료 → 발주대기 → 선적완료 → 항해중 → 통관중 → 배차완료
```
> ⚠️ 위 7개 값 외의 문자열을 입력하면 단계 뱃지 색상이 표시되지 않습니다.

**negotiation.status 허용값:** `진행중` / `완료`

**customs.status / dispatch.status 허용값:** `대기중` / `진행중` / `완료`

**오더 구조 예시:**
```json
{
  "id": "ORD-2026-006",
  "product": "PP Homo",
  "grade": "H380F",
  "supplier": "공급사명",
  "origin": "원산지",
  "quantity": 500,
  "unit": "MT",
  "stage": "네고중",
  "negotiation": {
    "status": "진행중",
    "offerPrice": 1020,
    "counterPrice": 995,
    "contractPrice": null,
    "currency": "USD/MT",
    "marketRef": 1010,
    "date": "2026-06-11"
  },
  "contract": {
    "contractNo": "",
    "signDate": "",
    "paymentTerms": "",
    "incoterms": "CFR Busan",
    "deliveryMonth": "2026-08"
  },
  "shipment": {
    "vessel": "",
    "blNo": "",
    "etd": "",
    "eta": "",
    "portOfLoading": "",
    "portOfDischarge": "부산"
  },
  "customs": {
    "arrivalDate": "",
    "declarationDate": "",
    "clearanceDate": "",
    "status": "대기중"
  },
  "dispatch": {
    "status": "대기중",
    "date": "",
    "destination": ""
  }
}
```

### 재고 수정
`data/data.json`의 `inventory` 배열에서 품목별 수치를 직접 수정합니다.

```json
{
  "product": "PP Homo",
  "currentStock": 320,
  "safetyStock": 200,
  "incomingStock": 500,
  "outgoingPlan": 150,
  "unit": "MT",
  "avgDailyUsage": 18,
  "location": "울산 창고"
}
```

### 최종 업데이트 날짜 수정
`data/data.json` 첫 줄의 `lastUpdated` 값을 변경합니다.
```json
{ "lastUpdated": "2026-06-11", ... }
```

---

## 에이전트 활용 (Claude Code)

Claude Code를 사용하는 경우 아래 에이전트와 스킬을 활용할 수 있습니다.

| 에이전트/스킬 | 호출 방법 | 용도 |
|-------------|----------|------|
| `resin-data-validator` | "데이터 검증해줘" | data.json stage·날짜·필드 자동 검증 |
| `dashboard-dev` | "dashboard-dev로 고쳐줘" | index.html 버그 수정 및 기능 추가 |
| `doc-reviewer` | "문서 검토해줘" | README·CLAUDE.md 품질 점검 |
| `data-update` 스킬 | "data-update 스킬 써줘" | 오더/재고 입력 가이드 + 템플릿 제공 |
| `briefing-improver` 스킬 | "briefing-improver" | 버그 발견 → 수정 → 문서화 전체 자동화 |

> `data.json` 저장 시 허용되지 않는 stage 값이 있으면 훅이 자동으로 차단합니다.

---

## 3인 협업 방법

1. GitHub에서 `data/data.json` 파일 클릭
2. 우측 상단 ✏️ 연필 아이콘 클릭 → 수정
3. **Commit changes** 버튼으로 저장
4. `index.html`을 새로고침하면 변경 내용 반영

> `index.html`은 수정할 필요 없습니다. 데이터만 `data.json`에서 관리합니다.

> ⚠️ **동시 편집 주의**: 3명이 같은 시간에 수정하면 GitHub에서 충돌이 발생할 수 있습니다.  
> 수정 전 항상 최신 버전을 확인하고, 한 명이 commit한 뒤 다음 사람이 편집하세요.

---

## 품목 목록

| 품목 | 안전재고 기준 | 창고 |
|------|-------------|------|
| PP Homo | 200 MT | 울산 |
| PP Copo | 150 MT | 부산 |
| HDPE | 180 MT | 인천 |
| LDPE | 100 MT | 울산 |
| LLDPE | 120 MT | 울산 |

---

## 빠른 실행 (서버 자동 시작)

```powershell
cd C:\path\to\resin-tracker
.\start-server.ps1
```

→ 브라우저에서 `http://localhost:8080/index.html` 접속

---

## 트러블슈팅 FAQ

### Q1: 대시보드에 데이터가 안 나타나요
**A:** `fetch()` 는 HTTP 서버가 필요합니다. `file://`로 열면 항상 빈 화면입니다.
- `start-server.ps1` 실행 후 `http://localhost:8080/index.html` 접속
- 브라우저 개발자도구(F12) → Console 탭에서 오류 메시지 확인

### Q2: 서버 실행 시 "포트 8080이 사용 중" 오류
**A:** 다른 프로그램이 해당 포트를 점유 중입니다.
```powershell
$py = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
& $py -m http.server 9090   # 다른 포트 사용
```
→ `http://localhost:9090/index.html` 접속

### Q3: 한글이 깨져서 나타나요 (???)
**A:** `data.json` 인코딩 문제입니다.
- VS Code에서 `data.json` 열기 → 우측 하단 인코딩 확인
- **UTF-8 (BOM 없음)** 으로 저장 권장
- Windows 메모장으로 저장한 경우 UTF-16이 될 수 있으니 주의

### Q4: 단계 뱃지 색상이 회색으로만 나와요
**A:** `stage` 필드에 오타가 있거나 공백이 포함된 것입니다.
- 허용값: `네고중` / `계약완료` / `발주대기` / `선적완료` / `항해중` / `통관중` / `배차완료`
- `data.json` 저장 시 `validate-stage.ps1` 훅이 자동으로 잡아줍니다
- Claude Code 외부에서 수정한 경우 오타를 직접 확인하세요

### Q5: 차트가 빈 화면으로 나타나요
**A:** Chart.js CDN 로드 실패 또는 데이터 구조 오류입니다.
- 인터넷 연결 확인 (CDN: `cdn.jsdelivr.net`)
- 브라우저 캐시 초기화: `Ctrl+Shift+Delete` → 하드 새로고침 `Ctrl+Shift+R`
- `marketPrices` 배열이 `data.json`에 존재하는지 확인

### Q6: 3명이 동시에 수정하면 어떻게 되나요?
**A:** GitHub에서 편집 충돌이 발생합니다.
- 수정 전 항상 GitHub에서 최신 버전 확인
- 한 명이 **Commit** 완료 후 다음 사람이 수정
- 충돌 발생 시 GitHub UI에서 충돌 해결 필요

---

## 새 오더 추가 예제

### 시나리오: HDPE 250MT 네고 시작 (ORD-2026-010)

#### 1단계: `data/data.json` 열기
- VS Code에서 `resin-tracker/data/data.json` 열기
- 또는 GitHub → `data/data.json` → ✏️ 편집

#### 2단계: `orders` 배열 끝에 아래 객체 추가

> **주의:** 직전 오더 객체 닫는 `}` 뒤에 **쉼표** 추가 후 붙여넣기

```json
{
  "id": "ORD-2026-010",
  "product": "HDPE",
  "grade": "TR571M",
  "supplier": "SK Geo Centric",
  "origin": "한국",
  "quantity": 250,
  "unit": "MT",
  "stage": "네고중",
  "negotiation": {
    "status": "진행중",
    "offerPrice": 1015,
    "counterPrice": 1000,
    "contractPrice": null,
    "currency": "USD/MT",
    "marketRef": 990,
    "date": "2026-06-12"
  },
  "contract": {
    "contractNo": "",
    "signDate": "",
    "paymentTerms": "",
    "incoterms": "CFR Incheon",
    "deliveryMonth": "2026-08"
  },
  "shipment": {
    "vessel": "",
    "blNo": "",
    "etd": "",
    "eta": "",
    "portOfLoading": "",
    "portOfDischarge": "인천"
  },
  "customs": {
    "arrivalDate": "",
    "declarationDate": "",
    "clearanceDate": "",
    "status": "대기중"
  },
  "dispatch": {
    "status": "대기중",
    "date": "",
    "destination": "안산 공장"
  }
}
```

#### 3단계: `lastUpdated` 날짜 업데이트
```json
"lastUpdated": "2026-06-12"
```

#### 4단계: 저장 → 브라우저 새로고침 (F5)

대시보드 탭에서 새 오더가 `네고중` 뱃지로 나타납니다.

#### 단계 진행 예시 — 계약완료 시

```json
"stage": "계약완료",
"negotiation": {
  "status": "완료",
  "contractPrice": 1005
},
"contract": {
  "contractNo": "C-2026-HDPE-002",
  "signDate": "2026-06-15",
  "paymentTerms": "T/T 30days"
}
```

**주의사항:**
- `stage` 값은 정확히 7개 중 하나 (공백·오타 X)
- 빈 필드는 `""` (빈 문자열), null 가능 필드는 `null`
- 금액·수량은 숫자형: `1005` (O), `"1005"` (X)
- 날짜는 `"YYYY-MM-DD"` 형식

---

## Railway 배포 (클라우드 공유)

팀원과 URL로 공유하려면 Railway에 배포하세요.

### 배포 단계

**1. GitHub push**
```powershell
git add resin-tracker/
git commit -m "resin-tracker: Railway 배포 준비"
git push origin main
```

**2. Railway 프로젝트 생성**
1. [railway.app](https://railway.app) 로그인
2. New Project → Deploy from GitHub → 저장소 선택
3. Settings → **Root Directory = `resin-tracker`** 설정

**3. 환경변수 등록** (Railway Dashboard → Variables)
```
EMAIL_FROM     = your@gmail.com
EMAIL_PASSWORD = 앱비밀번호16자리
EMAIL_TO       = receiver@company.com
SMTP_HOST      = smtp.gmail.com
SMTP_PORT      = 587
```

**4. 배포 완료** — Railway가 자동으로 `pip install -r requirements.txt` → `python app.py` 실행  
공개 URL 발급 (예: `https://resin-tracker-xxx.railway.app`)

### 주의
- `data.json`은 재배포 시 초기화됨 — 중요 데이터는 엑셀로 백업 후 배포
- PORT는 Railway가 자동 지정 (별도 설정 불필요)

---

## 변경 이력

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| v3.0 | 2026-06-12 | Flask 백엔드 전환, 엑셀 내보내기, 이메일 알림, python-dotenv 보안, Railway 배포 가이드 |
| v2.0 | 2026-06-12 | 에이전트 하네스 구조 추가 (3 agents + hooks + skills), 트러블슈팅 FAQ, 서버 자동시작 스크립트, 빈 상태 메시지, 상수화(ALERT_DAYS 등), 인쇄 CSS |
| v1.0 | 2026-06-01 | 초기 구성: 7탭 대시보드, data.json 기반 데이터 관리 |
