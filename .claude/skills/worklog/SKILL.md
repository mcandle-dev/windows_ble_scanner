---
name: worklog
description: 세션 종료 시 작업 기록을 남긴다 — CHANGELOG.md 갱신 + logs/work_log_YYYY-MM-DD.md 작성. 사용자가 "작업 기록해줘", "오늘 작업 정리", "worklog"라고 하거나 유의미한 구현을 마쳤을 때 사용.
---

# Worklog — 작업 기록

이 세션에서 수행한 변경을 리포 관례에 맞게 기록한다.

## 절차

1. `git log`와 이 세션의 변경 내역으로 오늘 작업을 파악한다.
2. **CHANGELOG.md**: 최상단에 `## [YYYY-MM-DD]` 섹션을 추가(이미 있으면 병합)하고
   Added / Changed / Fixed 소제목 아래 항목을 기록한다. 기존 항목의 문체(영문, 굵은 키워드 시작)를 따른다.
3. **logs/work_log_YYYY-MM-DD.md**: 기존 work_log 형식을 따라 작성한다:
   - `## 1. Accomplishments` — 완료한 것
   - `## 2. Technical Challenges & Fixes` — 부딪힌 문제와 해결
   - `## 3. Current State` — 현재 상태 (어떤 spec의 어느 태스크까지 왔는지)
   - `## 4. Tomorrow's Goals` — 다음 세션 목표 (남은 tasks 참조)
4. 진행 중인 spec이 있으면 해당 `tasks.md` 체크 상태가 실제와 일치하는지 확인하고 맞춘다.
5. 커밋은 사용자가 요청한 경우에만 수행한다.
