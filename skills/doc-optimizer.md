# Skill: doc-optimizer

## 목적
프로젝트 문서(README, data.json 구조, CLAUDE.md)를 검토하고 명확성·완결성·일관성 기준으로 개선한다.

## 실행 절차

1. **문서 파일 읽기**
   - `resin-tracker/README.md`
   - `resin-tracker/data/data.json` (구조 파악용)
   - `CLAUDE.md` (프로젝트 지침과 문서가 일치하는지 교차 확인)

2. **검토 기준**

   | 항목 | 체크 내용 |
   |------|----------|
   | 완결성 | 모든 탭 기능이 설명되어 있는가? data.json 모든 필드가 문서화되어 있는가? |
   | 명확성 | 비개발자(다른 부서)가 읽었을 때 바로 이해 가능한가? |
   | 실행 가능성 | 실행 방법이 단계별로 정확한가? 경로·명령어가 현재 환경에 맞는가? |
   | 일관성 | README의 stage 목록이 index.html의 STAGE_ORDER와 일치하는가? |
   | 협업 가이드 | 3인이 data.json을 충돌 없이 수정하는 방법이 명확한가? |

3. **개선 사항 적용**
   - README.md 직접 수정 (Edit 툴 사용)
   - 변경 내용 간략히 설명 후 GitHub에 push

   ```powershell
   # README 업데이트 push
   $headers = @{ "Authorization"="Bearer $token"; "Accept"="application/vnd.github+json"; "X-GitHub-Api-Version"="2022-11-28" }
   $file = Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/contents/README.md" -Headers $headers
   $sha = $file.sha
   $content = [System.IO.File]::ReadAllBytes("C:\Temp\ai-workshop\resin-tracker\README.md")
   $b64 = [Convert]::ToBase64String($content)
   $body = @{ message = "Docs: optimize README clarity and completeness"; content = $b64; sha = $sha } | ConvertTo-Json
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
   Invoke-RestMethod -Uri "https://api.github.com/repos/dsrcorp1-jpg/2/contents/README.md" `
       -Method Put -Headers $headers -Body $bytes -ContentType "application/json; charset=utf-8"
   ```

4. **개선 결과 보고**
   - 변경된 섹션 목록
   - 변경 전 → 변경 후 핵심 차이점 요약

## 주의
- 내용 삭제보다 명확화 위주로 편집
- 기술 정확도가 낮은 내용(잘못된 경로, 오래된 명령어)은 반드시 수정
- CLAUDE.md에 이미 있는 내용은 README에서 중복 제거 가능
