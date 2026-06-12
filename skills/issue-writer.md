# Skill: issue-writer

## 목적
현재 프로젝트(대시보드 HTML, data.json, README)를 분석해 약점·버그·개선점을 찾아 GitHub Issues로 등록한다.

## 실행 절차

1. **분석 대상 파일 읽기**
   - `resin-tracker/index.html` — UI 로직, 탭별 렌더링, 데이터 연결
   - `resin-tracker/data/data.json` — 데이터 구조 완결성
   - `resin-tracker/README.md` — 문서 누락 여부

2. **약점 목록 작성**
   아래 기준으로 검토:
   - 데이터가 없거나 null일 때 UI가 깨지는 경우
   - 탭 간 정보 불일치 (예: 재고 탭과 대시보드 알림이 다른 기준 사용)
   - 사용자가 실수하기 쉬운 data.json 필드 (예: stage 오타 허용)
   - README에서 설명이 빠진 기능
   - 다른 부서가 봤을 때 이해하기 어려운 UI 요소

3. **GitHub Issue 등록**
   저장소: `dsrcorp1-jpg/2`
   PAT 토큰은 대화 컨텍스트에서 재사용. 없으면 사용자에게 요청.

   각 이슈 형식:
   ```
   제목: [카테고리] 한 줄 설명
   본문:
   ## 문제
   ...
   ## 재현 방법 또는 위치
   ...
   ## 제안 해결책
   ...
   ```
   카테고리: `[Bug]`, `[UX]`, `[Data]`, `[Docs]`

4. **등록 결과 보고**
   - 등록된 이슈 번호와 제목 목록 출력
   - 우선순위 (High/Medium/Low) 함께 표시

## PowerShell GitHub API 패턴
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$payload = '{"title":"제목","body":"본문","labels":["bug"]}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/issues" `
    -Method Post -Headers $headers -Body $bytes -ContentType "application/json; charset=utf-8"
```

## 주의
- 이미 같은 내용의 이슈가 열려 있으면 중복 등록하지 않는다
- 이슈 본문에 한글 포함 시 반드시 UTF-8 바이트 변환 사용
