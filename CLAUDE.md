# CLAUDE.md — PP/PE 레진 단가 추적 프로젝트

이 파일은 Claude Code가 이 저장소에서 작업할 때 항상 참고하는 프로젝트 지침입니다.

---

## 프로젝트 개요

원재료 구매팀(PP/PE 레진 담당)을 위한 **단가 분석·추적·자동화** 시스템.  
ICIS/Platts 기준가 모니터링 → 공급사 오퍼 비교 → 계약 단가 관리 → 월간 자동 리포트 생성.

---

## 환경

| 항목 | 값 |
|------|----|
| OS | Windows 11 / PowerShell 5.1 |
| Python | `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe` |
| Git remote | `https://github.com/dsrcorp1-jpg/1` |
| 기본 브랜치 | `main` |

**PowerShell에서 Python 실행 시 항상 전체 경로 사용:**
```powershell
$py = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
& $py script.py
```

---

## 핵심 파일 구조

```
pp_pe_resin_report_v3.html   ← 최종 통합 리포트 (9섹션, Chart.js)
pp_pe_resin_report_v2.html   ← v2 (차트 추가, 환율 분석)
pp_pe_resin_report.html      ← v1 (정적 분석 기준 문서)
PP_PE_레진_단가추적.xlsx      ← Excel 4시트 단가추적 워크북
build_resin_tracker.py       ← Excel 워크북 생성 스크립트 (openpyxl)
reports/
  fetch_market_data.py       ← 시장 데이터 API 수집 스크립트
  API_KEY_SETUP.md           ← API 키 발급·등록 가이드
.github/workflows/
  monthly-report.yml         ← 매월 1일 자동 업데이트 워크플로우
```

---

## 주요 패턴 및 규칙

### 1. GitHub API — 한글 UTF-8 인코딩

`gh` CLI 없음. 항상 `Invoke-RestMethod` 사용. 한글 포함 시 반드시 UTF-8 바이트 변환:

```powershell
$headers = @{
    "Authorization"        = "Bearer $token"
    "Accept"               = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

# 한글 포함 페이로드
$payload = '{"body":' + ($body | ConvertTo-Json) + '}'
$bytes   = [System.Text.Encoding]::UTF8.GetBytes($payload)
Invoke-RestMethod -Uri $url -Method Post -Headers $headers `
    -Body $bytes -ContentType "application/json; charset=utf-8"
```

> `ConvertTo-Json`만 쓰면 한글이 깨짐 (PS 5.1에서 `-EscapeHandling` 미지원).

### 2. Excel 작업 (openpyxl)

- 수식은 반드시 문자열 공식(`"=SUM(A1:B1)"`)으로 저장 — Python에서 직접 계산하지 말 것
- `recalc.py`는 `socket.AF_UNIX` 의존성으로 Windows에서 실행 불가 → 건너뜀
- 색상 코딩: 입력셀 파란색(`0000FF`), 수식셀 검은색(`000000`)

### 3. HTML 리포트 (Chart.js)

- CDN: `chart.js@4.4.0` + `chartjs-plugin-annotation@3.0.1`
- 이중 Y축 차트에서 `yAxisID:'y'`/`'y2'` 반드시 지정
- 한국어 레이블 포함 시 `font-family: 'Segoe UI', 'Apple SD Gothic Neo', sans-serif`

### 4. Python 스크립트 (reports/)

- `fetch_market_data.py` — CLI: `--year`, `--month`, `--dry-run`, `--force`, `--backfill N`
- API 키는 환경변수(`EIA_API_KEY`, `BOK_API_KEY`, `ICIS_API_KEY`, `PLATTS_API_KEY`)
- 키 미설정 시 자동으로 근사치 공식 사용 (Platts 미설정 → `brent × 7.35 × 0.85`)

---

## 가격 데이터 레퍼런스

| 품목 | 최근 참고가 | 기준 |
|------|------------|------|
| PP Homo | $1,010/MT | ICIS CFR Asia |
| PP Copo | $1,070/MT | ICIS CFR Asia |
| HDPE | $990/MT | ICIS CFR Asia |
| LDPE | $1,060/MT | ICIS CFR Asia |
| LLDPE | $970/MT | ICIS CFR Asia |
| 나프타 | $630/MT | CFR Japan |
| Brent | $74/배럴 | ICE |
| USD/KRW | 1,380원 | 한국은행 |

**나프타 연동 PP 산정 공식 (협의 기준):**
```
PP 계약가 = 나프타(CFR Japan 당월 평균) × 1.55 + $85(고정마진) + $20(물류)
예시: $630 × 1.55 + $85 + $20 = $1,072/MT
```

---

## 커밋 메시지 규칙

```
[작업 요약 — 이슈 또는 기능 명시]

세부 변경 내용:
- 추가/수정/삭제한 파일
- 주요 기능 변경 사항

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## GitHub Issues 처리

이 저장소의 이슈 처리는 **`github-issue-workflow` 스킬**로 자동화됨.  
"이슈 처리해줘" 또는 "handle issues"라고 말하면 스킬이 자동 실행됨.

PAT 토큰은 대화 컨텍스트에 있으면 재사용. 없으면 사용자에게 요청.

---

## 하지 말 것

- `git push --force` 사용 금지
- `git add -A` 대신 파일명 명시적 스테이징 사용
- openpyxl로 수식 결과값을 Python에서 계산 후 하드코딩 금지
- `ConvertTo-Json`으로 한글 JSON 직접 전송 금지 (UTF-8 바이트 변환 필수)
