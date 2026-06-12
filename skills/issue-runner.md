# Skill: issue-runner

## 목적
GitHub에 열린 이슈를 확인하고, 우선순위 순으로 작업을 수행한 뒤 이슈를 닫는다.

## 실행 절차

1. **열린 이슈 목록 조회**
   ```powershell
   $headers = @{
       "Authorization" = "Bearer $token"
       "Accept" = "application/vnd.github+json"
       "X-GitHub-Api-Version" = "2022-11-28"
   }
   $issues = Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/issues?state=open" -Headers $headers
   $issues | ForEach-Object { Write-Output "#$($_.number) $($_.title)" }
   ```

2. **우선순위 결정**
   - `[Bug]` 라벨 → High (먼저 처리)
   - `[UX]` 라벨 → Medium
   - `[Data]` / `[Docs]` 라벨 → Low
   - 라벨 없으면 제목 내용 기반으로 판단

3. **이슈별 작업 수행**
   대상 파일:
   - `C:\Temp\ai-workshop\resin-tracker\index.html`
   - `C:\Temp\ai-workshop\resin-tracker\data\data.json`
   - `C:\Temp\ai-workshop\resin-tracker\README.md`

   작업 후 로컬 파일을 수정하고, GitHub API로 업데이트:
   ```powershell
   # SHA 먼저 조회 후 PUT으로 업데이트
   $file = Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/contents/index.html" -Headers $headers
   $sha = $file.sha
   $content = [System.IO.File]::ReadAllBytes("C:\Temp\ai-workshop\resin-tracker\index.html")
   $b64 = [Convert]::ToBase64String($content)
   $body = @{ message = "Fix: 이슈 제목"; content = $b64; sha = $sha } | ConvertTo-Json
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
   Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/contents/index.html" `
       -Method Put -Headers $headers -Body $bytes -ContentType "application/json; charset=utf-8"
   ```

4. **이슈 닫기**
   ```powershell
   $closeBody = '{"state":"closed","state_reason":"completed"}'
   $closeBytes = [System.Text.Encoding]::UTF8.GetBytes($closeBody)
   Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/issues/$issueNumber" `
       -Method Patch -Headers $headers -Body $closeBytes -ContentType "application/json; charset=utf-8"
   ```

5. **처리 결과 보고**
   - 완료된 이슈: `✅ #번호 제목`
   - 건너뛴 이슈(복잡도 높아 별도 확인 필요): `⏸ #번호 제목 — 이유`

## 주의
- 한 번에 처리할 이슈 수가 많으면 High 우선순위 것만 먼저 처리하고 나머지는 보고
- 파일 수정 전 반드시 현재 SHA를 조회해서 충돌 방지
- 한글 포함 커밋 메시지·이슈 본문은 UTF-8 바이트 변환 필수
