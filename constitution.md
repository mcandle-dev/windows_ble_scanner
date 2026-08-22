# Constitution — windows_ble_scanner

이 문서는 이 리포지토리의 **불변 원칙**이다. 기존 문서(`requirements.md`, `README.md`, 작업 로그)와
코드에서 반복적으로 지켜져 온 규칙을 승격한 것으로, 모든 spec/plan/tasks 및 코드 변경은
이 원칙을 위반할 수 없다. 원칙을 바꾸려면 이 문서를 먼저 수정하는 PR로 합의해야 한다.

## 제1조 — 비동기 우선 (Async-First)

- 모든 BLE 작업(스캔, 연결, 읽기, 쓰기, 해제)은 `asyncio` 기반 비동기로 처리한다.
- UI 스레드를 블로킹하는 BLE 호출은 금지한다. UI 프리징은 결함이다.
- 이벤트 핸들러에서 코루틴을 실행할 때는 `page.run_task()`를 사용한다
  (await 없이 코루틴을 방치해 `RuntimeWarning`을 유발하는 패턴 금지).

## 제2조 — 방어적 예외 처리 (Defensive by Default)

- Windows 블루투스 스택(WinRT)은 예측 불가능하게 실패한다. 모든 BLE 호출은 예외 처리로 감싼다.
- 어떤 BLE 오류도 앱을 크래시시켜서는 안 된다. 오류는 Activity Logs와 상태 표시줄로 사용자에게 보여준다.
- `Access Denied` 류의 보안 오류는 삼키지 말고, 원인(페어링/본딩 필요)을 사용자에게 안내한다.
- 연결 상태 전환(스캔 중지, 새 연결 시작) 시 기존 연결을 **명시적으로 해제**하여
  좀비 연결을 남기지 않는다.

## 제3조 — 관측 가능성 (Observability)

- 의미 있는 모든 이벤트(스캔 발견, 디코딩 결과, GATT 탐색, 송수신, 오류)는
  타임스탬프와 함께 Activity Logs에 기록한다.
- GATT 탐색 시 발견된 모든 Service/Characteristic UUID와 속성을 로깅한다.
- 로그는 `logs/ble_YYYYMMDD_HHMMSS.txt` 형식으로 로컬 저장 가능해야 한다.

## 제4조 — 단순성 (MVP Simplicity)

- 이 프로젝트는 MVP다. 복잡도가 명확히 요구되기 전까지 단일 파일(`main.py`) 구조를 유지한다.
- 모듈 분리는 spec으로 합의된 경우에만 수행하며, 분리하더라도 명확한 모듈 구조여야 한다.
- 추측성 추상화(사용처 없는 인터페이스, 설정 계층)를 금지한다.

## 제5조 — 버전 견고성 (Version Robustness)

- Flet은 마이너 버전 간 파괴적 변경이 잦다(0.80.x에서 확인됨). 버전에 취약한 API를 피한다:
  - 색상·아이콘은 가능한 한 문자열 리터럴로 지정한다.
  - `FilePicker`처럼 초기화가 불안정한 컨트롤 대신 직접 파일 I/O를 사용한다.
- 의존성은 `requirements.txt`에 버전을 고정(pin)한다.

## 제6조 — 인코딩 스펙 호환성 (Advertiser Spec Compatibility)

- 데이터 디코딩은 [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser)의
  Service UUID 임베딩 방식과 호환을 유지해야 한다:
  1. **Literal Hex 우선**: UUID `8-4-4-4-12` 중 앞 3개 세그먼트(16자리)=전화번호,
     4번째 세그먼트(4자리)=카드번호.
  2. **ASCII Fallback**: UUID 전체 hex를 ASCII로 변환 후 정규식 탐색
     (전화번호 `010\d{8}`, 카드번호 `\d{8,16}`).
- GATT 채널은 고정 UUID(`fff1` Write, `fff2` Read) 정합을 우선하고,
  없으면 속성 기반 fallback으로 선택한다. 시스템 특성(`2a00`, `2a01`, `2a05`, `2b29`, `2b2a`)은
  대상에서 제외한다.

## 제7조 — 문서 및 기록

- 사용자 대상 문서는 한국어를 기본으로 작성한다.
- 유의미한 변경은 `CHANGELOG.md`에 기록한다.
- 세션 단위 작업 기록은 `logs/work_log_YYYY-MM-DD.md`로 남긴다.

## 제8조 — SDD 거버넌스

- 새 기능·구조 변경은 `specs/NNN-<slug>/`에 **spec.md → plan.md → tasks.md** 순으로
  문서화한 뒤 구현한다.
- spec은 "무엇을·왜", plan은 "어떻게", tasks는 "실행 단위"만 다룬다. 역할을 섞지 않는다.
- 현행 시스템의 실체는 `DESIGN.md`가 단일 진실 공급원(SSOT)이며, 구현이 바뀌면 함께 갱신한다.
- 본 constitution은 spec/plan/tasks보다 우선한다.
