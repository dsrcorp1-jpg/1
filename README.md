# PP/PE 레진 단가 추적 시스템

원재료 구매팀을 위한 PP/PE 레진 가격 분석·추적·자동화 도구.  
유가 상관관계 분석부터 공급사 오퍼 비교, 월간 자동 데이터 수집까지.

> 이 프로젝트는 **Claude Code** (Anthropic)와 협업하여 구축되었습니다.  
> [Claude Code 공식 문서 →](https://docs.anthropic.com/en/docs/claude-code/overview)

---

## 빠른 시작

### 리포트 열기
```
pp_pe_resin_report_v3.html   ← 브라우저에서 바로 열기 (설치 불필요)
```

### Excel 단가추적 시트 열기
```
PP_PE_레진_단가추적.xlsx   ← Excel에서 열기
```

---

## 주요 결과물

### 📊 pp_pe_resin_report_v3.html — 최종 통합 리포트

브라우저에서 바로 열리는 인터랙티브 HTML 리포트 (9개 섹션).

| 섹션 | 내용 |
|------|------|
| ① 가격 차트 | PP/PE 레진·유가·나프타 월간 추이 (2019–2025), 이벤트 마킹 |
| ② 환율 영향 | USD/KRW 환율 & PP 원화 환산가, 시나리오별 비용 충격 |
| ③ 유가 상관관계 | Brent vs PP/HDPE 산점도, 6개월 롤링 상관계수 |
| ④ 뉴스레터·소스 | ICIS·Platts·ChemOrbis 등 8개 소스, 구독 링크·비용 조건 |
| ⑤ 가격 영향 요인 | 원가 측(유가·나프타·환율) / 수급 측(중국·증설·정기보수) |
| ⑥ 주요 이벤트 | 연간 반복 이벤트 캘린더 + 텍사스 한파·러우전쟁 등 돌발 사례 |
| ⑦ 계약 단가 입력 | 공급사별 계약 단가 직접 입력 (브라우저 내, ICIS 대비 차이 자동 표시) |
| ⑧ 공급사 오퍼 비교 | 7개사 단가·납기·MOQ 비교 + 종합 평가 매트릭스 |
| ⑨ 단가 산정 방법론 | 나프타 연동 공식, 계약 유형, 조정 메커니즘 6단계 |

### 📁 PP_PE_레진_단가추적.xlsx — Excel 단가추적 워크북

| 시트 | 내용 |
|------|------|
| 월간단가입력 | 18개월 이력 + 스프레드·원화환산·MoM 변동 자동 계산 |
| 공급사오퍼비교 | 7개사 오퍼 vs ICIS 기준가 프리미엄/디스카운트 |
| 단가시뮬레이터 | 유가·나프타·환율 입력 → PP/PE 예상 단가 자동 산출 |
| KPI요약 | 최근 단가·스프레드 신호·매수/매도 판단 요약 |

### ⚙️ GitHub Actions 월간 자동화

매월 1일 오전 9시(KST) 자동 실행:
1. EIA·한국은행 API로 유가·환율 수집 (`reports/fetch_market_data.py`)
2. Excel 단가추적 시트 신규 월 행 자동 추가
3. 월간 체크리스트 GitHub Issue 자동 생성

---

## 파일 구조

```
.
├── pp_pe_resin_report_v3.html      # 최종 통합 리포트 (권장)
├── pp_pe_resin_report_v2.html      # v2 — 인터랙티브 차트
├── pp_pe_resin_report.html         # v1 — 정적 분석 기준 문서
├── PP_PE_레진_단가추적.xlsx         # Excel 단가추적 워크북
├── build_resin_tracker.py          # Excel 워크북 생성 스크립트
├── reports/
│   ├── fetch_market_data.py        # 시장 데이터 API 수집
│   ├── API_KEY_SETUP.md            # API 키 발급·등록 가이드
│   └── fetch_log.jsonl             # 수집 이력 로그
├── .github/workflows/
│   └── monthly-report.yml          # 월간 자동화 워크플로우
├── CLAUDE.md                       # Claude Code 프로젝트 지침
├── SOUL.md                         # 프로젝트 철학·방향
└── README.md                       # 이 파일
```

---

## API 키 설정 (자동화 활성화)

| API | 비용 | 용도 | 설정 시간 |
|-----|------|------|-----------|
| EIA Open Data | **무료** | Brent 유가 자동 수집 | 수 분 (즉시 발급) |
| 한국은행 ECOS | **무료** | USD/KRW 환율 자동 수집 | 1~2일 |
| S&P Global Platts | 유료 | 나프타 CFR Japan | 계약 필요 |
| ICIS | 유료 | PP/PE 레진 실가 | 계약 필요 |

**등록 방법:** GitHub 저장소 → Settings → Secrets and variables → Actions → `EIA_API_KEY`, `BOK_API_KEY` 등록

> 상세 절차: [`reports/API_KEY_SETUP.md`](reports/API_KEY_SETUP.md)

키 미설정 시 아래 근사치 공식으로 자동 대체:
```
나프타 ≈ Brent × 7.35 × 0.85
PP Homo ≈ 나프타 × 1.55 + $80
HDPE ≈ (나프타 + $220) × 1.28 + $80
```

---

## 단가 산정 공식 (핵심 참고)

```
PP 계약가 = 나프타(CFR Japan 당월 평균) × 1.55 + $85(고정마진) + $20(물류)
예시: $630 × 1.55 + $85 + $20 = $1,072/MT

PE 계약가 = 에틸렌 현물 × 1.30 + $75(고정마진) + $20(물류)
```

나프타 배율(1.45~1.65)과 고정 마진은 공급사와 협의로 결정.

---

## 주요 모니터링 지표

| 지표 | 의미 | 임계값 |
|------|------|--------|
| PP−나프타 스프레드 | PP 생산 마진 | $250 이하 → 감산 압력 |
| Brent vs PP 상관계수 (6M) | 유가 선행성 | r < 0.4 → 수급 요인 지배 |
| USD/KRW | 원화 환산 원가 | 1,400원 초과 → 환헤지 검토 |
| ICIS vs 계약가 괴리율 | 계약 적정성 | ±5% 초과 → 재협상 검토 |

---

## 개발 환경

- Python 3.12 (`C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe`)
- 의존성: `openpyxl`, `requests`, `pandas`
- GitHub API: `Invoke-RestMethod` (PowerShell 5.1, `gh` CLI 없음)
- HTML 차트: Chart.js 4.4.0 + chartjs-plugin-annotation 3.0.1 (CDN)

```powershell
# 의존성 설치
$py = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe"
& $py -m pip install openpyxl requests pandas

# Excel 워크북 재생성
& $py build_resin_tracker.py

# 수동 데이터 수집 (dry-run)
& $py reports\fetch_market_data.py --year 2025 --month 6 --dry-run
```

---

## 라이선스

내부 업무용 — 원재료 구매팀 전용.  
가격 데이터는 ICIS, Platts, ChemOrbis, 한국석유화학협회 참조 기반 재구성 시계열이며  
실거래가는 별도 확인이 필요합니다.

---

*Built with [Claude Code](https://claude.ai/code) by Anthropic*
