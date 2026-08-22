# KICKOFF_PROMPT — 새 세션 시작용 프롬프트 원본

새 Claude Code 세션을 시작할 때 아래 프롬프트를 복사해 붙여넣는다.
`<...>` 부분만 그 세션의 목표로 바꾼다.

---

```
이 리포는 SDD(Spec-Driven Development)로 운영된다. 작업 전에 다음 순서로 컨텍스트를 잡아라:

1. constitution.md — 불변 원칙. 모든 판단의 최우선 기준.
2. DESIGN.md — 현행 시스템 설계와 알려진 한계.
3. specs/ — 번호순으로 훑고, 상태가 "진행 중"인 spec의 tasks.md에서 남은 작업을 확인.
4. CHANGELOG.md 최상단 — 최근 변경 맥락.

이번 세션의 목표: <여기에 목표를 쓴다>

규칙:
- 목표가 새 기능/구조 변경이면: 구현 전에 specs/NNN-<slug>/에 spec.md → plan.md →
  tasks.md를 먼저 작성하고 나에게 확인받아라 (/sdd-feature 스킬 사용).
- 목표가 기존 spec의 이어하기면: 해당 tasks.md의 미완료 항목부터 진행하라.
- 구현 후에는 tasks 체크박스 갱신, DESIGN.md/CHANGELOG.md 반영, /worklog로 작업 기록.
- BLE 실기기 검증은 내가 한다. 검증 시나리오를 정리해서 알려달라.
- constitution과 충돌하는 요구가 생기면 멈추고 나에게 물어라.
```

---

## 자주 쓰는 목표 예시

- `이번 세션의 목표: specs/002-gatt-connection-stability의 남은 tasks(T3~T9)를 구현한다.`
- `이번 세션의 목표: Notify/Indicate 구독 기능의 spec을 새로 작성한다 (구현은 다음 세션).`
- `이번 세션의 목표: logs/ble_*.txt 최신 스캔 로그를 분석해 디코딩 실패 케이스를 찾는다.`
