# API 키 설정 가이드

GitHub Actions 자동 수집을 위해 아래 API 키를 저장소 Secrets에 등록합니다.

## 등록 경로
`GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret`

---

## 1. EIA Open Data API (무료) — Brent 유가

| 항목 | 내용 |
|------|------|
| 제공 데이터 | Brent 월평균 유가 (USD/배럴) |
| 비용 | 무료 |
| 발급 URL | https://www.eia.gov/opendata/register.php |
| Secret 이름 | `EIA_API_KEY` |

**발급 절차:**
1. eia.gov/opendata/register.php 접속
2. 이메일 입력 후 즉시 발급 (수 분 내)
3. 이메일로 전송된 API 키를 `EIA_API_KEY`에 등록

---

## 2. 한국은행 ECOS API (무료) — USD/KRW 환율

| 항목 | 내용 |
|------|------|
| 제공 데이터 | USD/KRW 월평균 환율 (원) |
| 비용 | 무료 |
| 발급 URL | https://ecos.bok.or.kr/api/#/AuthKeyApply |
| Secret 이름 | `BOK_API_KEY` |

**발급 절차:**
1. ecos.bok.or.kr 접속 → 인증키 신청
2. 공공기관/기업/개인 선택 후 신청 (1~2일 소요)
3. 발급된 인증키를 `BOK_API_KEY`에 등록

---

## 3. S&P Global Platts API (유료) — 나프타 CFR Japan

| 항목 | 내용 |
|------|------|
| 제공 데이터 | 나프타 CFR Japan 월평균 (USD/MT) |
| 비용 | 유료 (연간 계약) |
| 문의 URL | https://developer.spglobal.com/ |
| Secret 이름 | `PLATTS_API_KEY` |

> **키 미설정 시:** Brent × 7.35 × 0.85 근사치 자동 사용

---

## 4. ICIS Data API (유료) — PP/PE 레진 가격

| 항목 | 내용 |
|------|------|
| 제공 데이터 | PP Homo/Copo, HDPE, LDPE, LLDPE 아시아 CFR 월평균 |
| 비용 | 유료 (연간 계약) |
| 문의 URL | https://www.icis.com/explore/services/api/ |
| Secret 이름 | `ICIS_API_KEY` |

> **키 미설정 시:** 나프타 연동 공식 근사치 자동 사용
> - PP Homo = 나프타 × 1.55 + 80
> - HDPE    = (나프타 + 220) × 1.28 + 80

---

## 현재 수집 상태 요약

| API | 키 상태 | 데이터 품질 |
|-----|---------|------------|
| EIA (Brent) | ⬜ 미등록 | 등록 후 실제값 |
| 한국은행 (환율) | ⬜ 미등록 | 등록 후 실제값 |
| Platts (나프타) | ⬜ 미등록 | 근사치 사용 중 |
| ICIS (레진) | ⬜ 미등록 | 근사치 사용 중 |

EIA, 한국은행은 **무료**이므로 즉시 등록을 권장합니다.
