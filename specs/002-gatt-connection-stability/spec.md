# Spec 002 — GATT 연결 안정화 (Connection Stability)

- **상태**: 🚧 진행 중 (일부 구현됨 — 좀비 연결 방지는 db04a7b로 반영)
- **출처**: 작업 로그 2026-01-18 "Tomorrow's Goals: more robust GATT connection state management"
  및 CHANGELOG 2026-01-25 연결 로직 개선의 후속.
- **관련**: [plan.md](plan.md) · [tasks.md](tasks.md)

## 1. 배경 및 목적 (Why)

MVP의 연결 관리는 "연결 → 1회 읽기 → 쓰기" 수준이다. 실사용에서는 다음 문제가 남아 있다:

- 장치 측에서 연결이 끊겨도 앱이 감지하지 못하고 Send 버튼이 활성 상태로 남는다.
- 연결 실패·끊김 시 재시도 수단이 UI 재조작뿐이다.
- 페어링/본딩이 필요한 장치에서는 안내 메시지만 표시되고 흐름이 끊긴다.

연결 수명주기를 명시적으로 관리하여 도구로서의 신뢰성을 확보한다.

## 2. 사용자 시나리오

1. 연결된 장치가 꺼지거나 범위를 벗어나면, 앱이 즉시 "Disconnected"를 표시하고
   Send 버튼을 비활성화한다.
2. 연결 시도가 실패하면 제한된 횟수만큼 자동 재시도하고, 과정을 로그로 보여준다.
3. 사용자가 명시적으로 Disconnect 할 수 있다 (Connect의 대칭 동작).
4. Access Denied 발생 시 Windows 페어링 절차로 이어지는 구체적 안내를 받는다.

## 3. 기능 요구사항 (What)

| ID | 요구사항 | 수용 기준 |
|---|---|---|
| FR-1 | 연결 상태 명시화 | Idle/Connecting/Connected/Disconnected 상태가 UI·내부에서 일관됨 |
| FR-2 | 끊김 감지 | `BleakClient(disconnected_callback=...)`로 원격 끊김 즉시 반영, Send 비활성화 |
| FR-3 | 연결 재시도 | 연결 실패 시 N회(기본 2회) 백오프 재시도, 각 시도 로깅 |
| FR-4 | 명시적 Disconnect UI | 연결 중에는 Connect 버튼이 Disconnect로 전환 |
| FR-5 | 페어링 안내 개선 | Access Denied 시 페어링 절차 안내를 로그+상태줄에 표시 |
| FR-6 | 좀비 연결 방지 유지 | 기존 명시적 disconnect 동작 회귀 없음 (✅ 구현됨) |

## 4. 비기능 요구사항

- constitution 제1·2조 준수: 전 과정 비동기, 어떤 경로에서도 크래시 금지.
- 단일 파일 구조 유지 (제4조). 상태 관리가 비대해지면 모듈 분리를 별도 spec으로 제안.

## 5. 범위 제외 (Out of Scope)

- Notify/Indicate 구독 (별도 spec으로).
- 페어링 자동화(프로그래매틱 본딩) — Windows에서는 OS 다이얼로그 유도까지만.
- 다중 동시 연결.
