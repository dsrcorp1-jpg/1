"""
PP/PE 레진 시장 데이터 수집기
================================
[무료 공개 API — 즉시 사용 가능]
  - Brent 유가     : EIA Open Data API (무료 키 필요: eia.gov/opendata)
  - USD/KRW 환율   : 한국은행 ECOS API (무료 키 필요: ecos.bok.or.kr)
  - 나프타 근사치  : Brent × 0.85 (실제 Platts CFR Japan 연동 전 임시)

[유료 API — 계약 후 활성화]
  - PP/PE 레진 가격 : ICIS API  (환경변수 ICIS_API_KEY 설정 시 활성)
  - 나프타 정밀 가격: Platts API (환경변수 PLATTS_API_KEY 설정 시 활성)

사용법:
  python fetch_market_data.py [--year YYYY] [--month MM] [--dry-run]

환경변수 (GitHub Secrets → Actions 환경변수로 주입):
  EIA_API_KEY       : EIA Open Data API 키
  BOK_API_KEY       : 한국은행 ECOS API 키
  ICIS_API_KEY      : ICIS API 키 (선택, 유료)
  PLATTS_API_KEY    : S&P Global Platts API 키 (선택, 유료)
"""

import argparse
import csv
import datetime
import json
import os
import pathlib
import sys
import time

try:
    import requests
except ImportError:
    print("requests 패키지 필요: pip install requests")
    sys.exit(1)


# ─────────────────────────────────────────
# 설정
# ─────────────────────────────────────────
CSV_PATH   = pathlib.Path(__file__).parent / "market_data.csv"
LOG_PATH   = pathlib.Path(__file__).parent / "fetch_log.jsonl"

FIELDNAMES = [
    "label", "year", "month",
    "pp_homo", "pp_copo", "hdpe", "ldpe", "lldpe",
    "naphtha", "brent", "usdkrw",
    "pp_nap_spread", "pp_krw",
    "brent_source", "usdkrw_source", "naphtha_source", "resin_source",
    "updated_at",
]


# ─────────────────────────────────────────
# 1. Brent 유가 — EIA Open Data API (무료)
# ─────────────────────────────────────────
def fetch_brent_eia(year: int, month: int) -> dict:
    """
    EIA Open Data API v2 로 Brent 월평균 유가 조회.
    API 키: https://www.eia.gov/opendata/register.php (무료)
    """
    api_key = os.environ.get("EIA_API_KEY", "")
    if not api_key:
        return {"value": None, "source": "EIA_API_KEY 미설정"}

    start = f"{year}-{month:02d}"
    end   = f"{year}-{month:02d}"
    url = (
        "https://api.eia.gov/v2/petroleum/pri/spt/data/"
        f"?api_key={api_key}"
        "&frequency=monthly"
        "&data[0]=value"
        "&facets[product][]=EPCBRENT"
        f"&start={start}&end={end}"
        "&sort[0][column]=period&sort[0][direction]=desc"
        "&length=1"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json().get("response", {}).get("data", [])
        if data:
            val = round(float(data[0]["value"]), 2)
            return {"value": val, "source": "EIA Open Data API"}
    except Exception as e:
        return {"value": None, "source": f"EIA 오류: {e}"}
    return {"value": None, "source": "EIA 데이터 없음"}


# ─────────────────────────────────────────
# 2. USD/KRW 환율 — 한국은행 ECOS API (무료)
# ─────────────────────────────────────────
def fetch_usdkrw_bok(year: int, month: int) -> dict:
    """
    한국은행 ECOS API 로 USD/KRW 월평균 환율 조회.
    API 키: https://ecos.bok.or.kr/api/#/AuthKeyApply (무료)
    통계코드: 036Y001 (주요국통화의대원화환율)
    """
    api_key = os.environ.get("BOK_API_KEY", "")
    if not api_key:
        return {"value": None, "source": "BOK_API_KEY 미설정"}

    period = f"{year}{month:02d}"
    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr"
        f"/1/1/036Y001/MM/{period}/{period}/0000001"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        items = r.json().get("StatisticSearch", {}).get("row", [])
        if items:
            val = round(float(items[0]["DATA_VALUE"]), 0)
            return {"value": int(val), "source": "한국은행 ECOS API"}
    except Exception as e:
        return {"value": None, "source": f"BOK 오류: {e}"}
    return {"value": None, "source": "BOK 데이터 없음"}


# ─────────────────────────────────────────
# 3. 나프타 — Platts API (유료) 또는 Brent 근사
# ─────────────────────────────────────────
def fetch_naphtha_platts(year: int, month: int, brent: float) -> dict:
    """
    PLATTS_API_KEY 있으면 S&P Global Commodity Insights API 호출.
    없으면 Brent × 0.85 근사치 사용 (역사적 평균 비율).
    """
    api_key = os.environ.get("PLATTS_API_KEY", "")
    if api_key:
        # ── S&P Global Commodity Insights API (계약 후 활성화) ──
        # 참고: https://developer.spglobal.com/
        # 나프타 CFR Japan 심볼: AAWKF00 (물가지수) 또는 PUAAA00
        try:
            headers = {
                "appkey": api_key,
                "Content-Type": "application/json",
            }
            start = f"{year}-{month:02d}-01"
            end_day = 28 if month == 2 else 30
            end = f"{year}-{month:02d}-{end_day}"
            url = "https://api.platts.com/tradedata/v1/assessments/history"
            payload = {
                "symbol": ["AAWKF00"],
                "startDate": start,
                "endDate": end,
                "frequency": "monthly",
            }
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json().get("results", [])
            if data:
                val = round(float(data[0].get("value", 0)), 0)
                return {"value": int(val), "source": "S&P Global Platts API"}
        except Exception as e:
            pass  # 실패 시 근사치 사용

    # 근사치: Brent × 0.85 (USD/MT 환산, 1배럴 ≈ 0.136MT 나프타 기준)
    if brent:
        approx = round(brent * 7.35 * 0.85, 0)
        return {"value": int(approx), "source": f"Brent 근사치 (×7.35×0.85, PLATTS_API_KEY 미설정)"}
    return {"value": None, "source": "계산 불가"}


# ─────────────────────────────────────────
# 4. PP/PE 레진 — ICIS API (유료) 또는 플레이스홀더
# ─────────────────────────────────────────
def fetch_resin_icis(year: int, month: int, naphtha: float) -> dict:
    """
    ICIS_API_KEY 있으면 ICIS Data API 호출.
    없으면 나프타 연동 공식 근사치 반환.
    근사 공식 (역사적 배율):
      PP Homo  = 나프타 × 1.55 + 80
      PP Copo  = PP Homo + 60
      HDPE     = (나프타 + 220) × 1.28 + 80
      LDPE     = HDPE + 70
      LLDPE    = (나프타 + 220) × 1.25 + 80
    """
    api_key = os.environ.get("ICIS_API_KEY", "")
    if api_key:
        # ── ICIS Data API (계약 후 활성화) ──
        # 참고: https://www.icis.com/explore/services/api/
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            period = f"{year}-{month:02d}"
            commodities = {
                "pp_homo":  "PP-HOMO-INJECTION-ASIA-CFR",
                "pp_copo":  "PP-COPO-INJECTION-ASIA-CFR",
                "hdpe":     "HDPE-FILM-ASIA-CFR",
                "ldpe":     "LDPE-FILM-ASIA-CFR",
                "lldpe":    "LLDPE-C4-FILM-ASIA-CFR",
            }
            results = {}
            for key, symbol in commodities.items():
                url = f"https://api.icis.com/v1/prices/{symbol}?period={period}"
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.json()
                results[key] = round(float(data.get("midpoint", 0)), 0)
            results["source"] = "ICIS Data API"
            return results
        except Exception as e:
            pass  # 실패 시 근사치 사용

    # 나프타 연동 공식 근사치
    if naphtha:
        pp  = round(naphtha * 1.55 + 80, 0)
        hd  = round((naphtha + 220) * 1.28 + 80, 0)
        return {
            "pp_homo":  int(pp),
            "pp_copo":  int(pp + 60),
            "hdpe":     int(hd),
            "ldpe":     int(hd + 70),
            "lldpe":    int((naphtha + 220) * 1.25 + 80),
            "source":   "나프타 연동 공식 근사치 (ICIS_API_KEY 미설정)",
        }
    return {k: None for k in ["pp_homo","pp_copo","hdpe","ldpe","lldpe","source"]}


# ─────────────────────────────────────────
# 메인 로직
# ─────────────────────────────────────────
def load_csv() -> list:
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(rows: list):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_log(entry: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_and_update(year: int, month: int, dry_run: bool = False, force: bool = False):
    label = f"{str(year)[2:]}-{month:02d}"
    print(f"\n{'='*50}")
    print(f"수집 대상: {year}년 {month}월 ({label})")
    print(f"{'='*50}")

    rows = load_csv()

    # 중복 체크
    existing_idx = next((i for i, r in enumerate(rows) if r.get("label") == label), None)
    if existing_idx is not None and not force:
        print(f"[SKIP] {label} 이미 존재합니다. --force 옵션으로 덮어쓸 수 있습니다.")
        return rows[existing_idx]

    # ── 데이터 수집 ──
    print("\n[1/4] Brent 유가 수집 중...")
    brent_result = fetch_brent_eia(year, month)
    print(f"  → {brent_result['value']} USD/bbl  ({brent_result['source']})")

    time.sleep(0.5)
    print("[2/4] USD/KRW 환율 수집 중...")
    fx_result = fetch_usdkrw_bok(year, month)
    print(f"  → {fx_result['value']} 원  ({fx_result['source']})")

    time.sleep(0.5)
    print("[3/4] 나프타 가격 수집 중...")
    nap_result = fetch_naphtha_platts(year, month, brent_result["value"])
    print(f"  → {nap_result['value']} USD/MT  ({nap_result['source']})")

    time.sleep(0.5)
    print("[4/4] PP/PE 레진 가격 수집 중...")
    resin_result = fetch_resin_icis(year, month, nap_result["value"])
    print(f"  → PP Homo: {resin_result.get('pp_homo')}  ({resin_result.get('source')})")

    # ── 파생 지표 계산 ──
    pp   = resin_result.get("pp_homo")
    nap  = nap_result["value"]
    fx   = fx_result["value"]
    spread = round(pp - nap, 0) if pp and nap else None
    pp_krw = round(pp * fx, 0)  if pp and fx else None

    new_row = {
        "label":          label,
        "year":           year,
        "month":          month,
        "pp_homo":        pp,
        "pp_copo":        resin_result.get("pp_copo"),
        "hdpe":           resin_result.get("hdpe"),
        "ldpe":           resin_result.get("ldpe"),
        "lldpe":          resin_result.get("lldpe"),
        "naphtha":        nap_result["value"],
        "brent":          brent_result["value"],
        "usdkrw":         fx_result["value"],
        "pp_nap_spread":  spread,
        "pp_krw":         pp_krw,
        "brent_source":   brent_result["source"],
        "usdkrw_source":  fx_result["source"],
        "naphtha_source": nap_result["source"],
        "resin_source":   resin_result.get("source"),
        "updated_at":     datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # ── 결과 출력 ──
    print(f"\n{'─'*40}")
    print(f"  PP Homo     : {pp} USD/MT")
    print(f"  HDPE        : {resin_result.get('hdpe')} USD/MT")
    print(f"  나프타      : {nap} USD/MT")
    print(f"  Brent       : {brent_result['value']} USD/bbl")
    print(f"  USD/KRW     : {fx_result['value']} 원")
    print(f"  PP-나프타   : {spread} USD/MT")
    print(f"  PP 원화환산 : {pp_krw:,} 원/MT" if pp_krw else "  PP 원화환산 : -")
    print(f"{'─'*40}")

    log_entry = {**new_row, "dry_run": dry_run}
    append_log(log_entry)

    if dry_run:
        print("\n[DRY-RUN] CSV에 저장하지 않았습니다.")
        return new_row

    if existing_idx is not None:
        rows[existing_idx] = new_row
    else:
        rows.append(new_row)

    save_csv(rows)
    print(f"\n[OK] {CSV_PATH} 저장 완료 (총 {len(rows)}개월)")
    return new_row


def main():
    parser = argparse.ArgumentParser(description="PP/PE 레진 시장 데이터 수집기")
    parser.add_argument("--year",    type=int, default=None)
    parser.add_argument("--month",   type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="CSV 저장 없이 결과만 출력")
    parser.add_argument("--force",   action="store_true", help="기존 데이터 덮어쓰기")
    parser.add_argument("--backfill", type=int, default=0,
                        help="현재 월부터 N개월 전까지 소급 수집")
    args = parser.parse_args()

    now = datetime.datetime.utcnow()

    if args.backfill > 0:
        for i in range(args.backfill, -1, -1):
            target = now.replace(day=1) - datetime.timedelta(days=1) * (i * 28)
            fetch_and_update(target.year, target.month,
                             dry_run=args.dry_run, force=args.force)
            time.sleep(1)
    else:
        year  = args.year  or now.year
        month = args.month or now.month
        fetch_and_update(year, month, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
