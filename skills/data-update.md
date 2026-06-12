---
name: data-update
description: 오더 또는 재고 데이터를 data.json에 추가하거나 수정할 때 사용. stage 값 오타 방지, 필드 구조 가이드, 검증까지 포함.
argument-hint: [orders|inventory] [add|update]
allowed-tools: Read, Edit
---

## 현재 data.json 미리보기
!`powershell -Command "Get-Content -Raw 'C:\Temp\ai-workshop\resin-tracker\data\data.json' | ConvertFrom-Json | ConvertTo-Json -Depth 3"`

---

## 데이터 수정 절차

### Step 1 — 수정 범위 확인
사용자가 요청한 내용이 `orders` 배열인지 `inventory` 배열인지 확인합니다.

### Step 2 — 필드 검증 (수정 전)
**stage 허용값 (이 7개만 사용):**
```
네고중 → 계약완료 → 발주대기 → 선적완료 → 항해중 → 통관중 → 배차완료
```

**상태값:**
| 필드 | 허용값 |
|------|--------|
| `negotiation.status` | `진행중` / `완료` |
| `customs.status` | `대기중` / `진행중` / `완료` |
| `dispatch.status` | `대기중` / `진행중` / `완료` |

**날짜 형식:** `YYYY-MM-DD` (예: `2026-08-15`)
**연월 형식:** `YYYY-MM` (예: `2026-08`)

### Step 3 — 오더 추가 시 기본 템플릿
```json
{
  "id": "ORD-2026-XXX",
  "product": "PP Homo",
  "grade": "",
  "supplier": "",
  "origin": "",
  "quantity": 0,
  "unit": "MT",
  "stage": "네고중",
  "negotiation": {
    "status": "진행중",
    "offerPrice": null,
    "counterPrice": null,
    "contractPrice": null,
    "currency": "USD/MT",
    "marketRef": null,
    "date": ""
  },
  "contract": {
    "contractNo": "",
    "signDate": "",
    "paymentTerms": "",
    "incoterms": "CFR Busan",
    "deliveryMonth": ""
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

### Step 4 — 재고 수정 시 필드 구조
```json
{
  "product": "PP Homo",
  "currentStock": 0,
  "safetyStock": 0,
  "incomingStock": 0,
  "outgoingPlan": 0,
  "unit": "MT",
  "avgDailyUsage": 0,
  "location": ""
}
```

### Step 5 — 수정 후 확인
- `resin-data-validator` 에이전트를 활용해 변경된 항목 검증 권장
- `lastUpdated` 날짜를 오늘 날짜로 업데이트

---

## 품목 목록 참고
| 품목 | 안전재고 | 창고 |
|------|----------|------|
| PP Homo | 200 MT | 울산 |
| PP Copo | 150 MT | 부산 |
| HDPE | 180 MT | 인천 |
| LDPE | 100 MT | 울산 |
| LLDPE | 120 MT | 울산 |
