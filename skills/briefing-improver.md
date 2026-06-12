# Skill: briefing-improver

## 목적
PP/PE 레진 구매 관리 대시보드의 품질을 세 단계로 자동 개선한다.

```
[Step 1] issue-writer   — 약점 발견 → GitHub Issues 등록
[Step 2] issue-runner   — 이슈 확인 → 코드/데이터 수정 → 이슈 종료
[Step 3] doc-optimizer  — README·문서 검토 및 개선
```

세 절차를 순서대로 실행하되, 각 단계 완료 후 결과를 보고하고 다음 단계로 넘어간다.

---

## 실행 순서

### Step 1 — issue-writer 실행
`skills/issue-writer.md` 지침에 따라:
1. `index.html`, `data.json`, `README.md` 분석
2. 발견된 약점을 `dsrcorp1-jpg/2` 저장소에 GitHub Issues로 등록
3. 등록된 이슈 목록과 우선순위 보고

> Step 1 완료 후 메시지 예시:
> ```
> ✅ Step 1 완료 — 이슈 3건 등록
> #1 [Bug] stage 값 오타 시 뱃지 스타일 미적용
> #2 [UX] 재고 탭 — DOI 계산식 설명 없음
> #3 [Docs] README 실행 방법에 VS Code 경로 오류
> ```

---

### Step 2 — issue-runner 실행
`skills/issue-runner.md` 지침에 따라:
1. Step 1에서 등록된 이슈(+ 기존 열린 이슈) 조회
2. High → Medium → Low 순서로 처리
3. 파일 수정 후 GitHub push
4. 처리된 이슈 닫기
5. 처리 결과 보고

> Step 2 완료 후 메시지 예시:
> ```
> ✅ Step 2 완료
> ✅ #1 수정 완료 — stage 방어 코드 추가
> ✅ #3 수정 완료 — README 경로 수정
> ⏸ #2 보류 — UX 변경은 사용자 확인 후 진행
> ```

---

### Step 3 — doc-optimizer 실행
`skills/doc-optimizer.md` 지침에 따라:
1. README.md 완결성·명확성 검토
2. Step 2에서 바뀐 내용이 문서에 반영되었는지 확인
3. 개선 후 GitHub push
4. 변경 요약 보고

> Step 3 완료 후 메시지 예시:
> ```
> ✅ Step 3 완료 — README 2개 섹션 개선
> - 실행 방법: VS Code 경로 수정
> - 오더 구조: stage 허용값 목록 추가
> ```

---

## 최종 보고 형식

```
=== briefing-improver 완료 ===

Step 1 (issue-writer): 이슈 N건 등록
Step 2 (issue-runner): N건 수정 완료, N건 보류
Step 3 (doc-optimizer): 문서 N섹션 개선

GitHub: https://github.com/dsrcorp1-jpg/2
```

---

## 사전 조건
- PAT 토큰이 대화 컨텍스트에 있어야 함. 없으면 실행 전 사용자에게 요청.
- 로컬 파일 경로: `C:\Temp\ai-workshop\resin-tracker\`
- 저장소: `dsrcorp1-jpg/2`

## 참조 스킬
- [[issue-writer]] — `skills/issue-writer.md`
- [[issue-runner]] — `skills/issue-runner.md`
- [[doc-optimizer]] — `skills/doc-optimizer.md`
