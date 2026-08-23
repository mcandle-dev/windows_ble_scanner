# KICKOFF_PROMPT — 새 세션 시작용 프롬프트

새 Claude 세션(Opus 5 / Fable 5)을 시작할 때 아래 프롬프트를 복사해 사용한다.
`<...>` 부분만 채우면 된다.

---

```
이 리포는 SDD(Spec-Driven Development) 방식으로 개발한다.

시작 전에 다음 순서로 컨텍스트를 로드해:
1. constitution.md — 불변 원칙 (위반 금지)
2. DESIGN.md — 현행 시스템 설계
3. PEER_CONTRACT.md — 상대측(ble-advertiser) 계약
4. specs/ 에서 진행 중인 spec의 spec.md / plan.md / tasks.md

오늘 작업: <작업 내용 한 줄>

규칙:
- 새 기능이면 specs/NNN-<이름>/ 에 spec.md → plan.md → tasks.md 를 먼저 작성하고,
  내 승인을 받은 뒤 구현을 시작해.
- 기존 spec의 연속 작업이면 tasks.md의 미완 항목에서 이어가.
- 이 앱은 Windows + Bluetooth 실기기에서만 실행 가능하다. 네가 실행할 수 없는 환경이라면
  py_compile 수준의 정적 검증까지만 하고, 실기기 확인이 필요한 항목을 정리해서 알려줘.
- 작업을 마치면: tasks.md 체크 갱신 → CHANGELOG.md 기록 → (설계 변경 시) DESIGN.md 갱신
  → logs/work_log_YYYY-MM-DD.md 작성.
```

---

## 변형: 버그 수정 세션

```
constitution.md 와 DESIGN.md 를 읽고 시작해.

버그: <증상>
재현: <재현 방법 / 로그 파일 경로 (logs/ble_*.txt)>

연결·전송·디코딩 관련이면 먼저 ble-peer-analyst 에이전트로 상대측(ble-advertiser) 계약이
깨지지 않았는지 확인하고 시작해.

spec 없이 바로 수정하되, constitution의 원칙(비동기, 명시적 disconnect, 방어적 예외 처리,
Flet 0.80.x 호환)을 지키고, 수정 후 CHANGELOG.md에 기록해.
```

---

## 변형: 상대측 변경 확인

```
ble-peer-analyst 에이전트를 실행해서 ble-advertiser(Android) 계약이
PEER_CONTRACT.md와 달라진 게 있는지 확인해줘.

차이가 있으면 PEER_CONTRACT.md를 갱신하고, main.py가 영향받는 부분을 알려줘.
```
