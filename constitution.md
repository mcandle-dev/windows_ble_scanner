# Constitution — windows_ble_scanner

이 문서는 이 리포지토리의 **불변 원칙**이다. 여기 명시된 원칙은 개별 spec/plan/tasks 보다 우선하며,
변경하려면 이 파일 자체를 수정하는 명시적 결정이 필요하다.
(출처: `requirements.md` §4 개발 제약, README, `main.py` 구현 관행에서 승격)

## 1. 비동기 우선 (Async-First)

- 모든 BLE 작업(스캔, 연결, 읽기, 쓰기)은 `asyncio` 기반 비동기로 처리한다. **UI 프리징은 결함이다.**
- Flet 이벤트 핸들러에서 코루틴을 직접 호출하지 않는다 — `page.run_task()`로 실행한다.

## 2. 단순성 (Simplicity)

- 애플리케이션은 **단일 파일 `main.py`** 를 유지한다. 모듈 분리는 단일 파일이 명백히 감당 불가능해진
  시점에, spec으로 합의된 후에만 한다.
- MVP 정신 유지: 요구되지 않은 추상화·설정·옵션을 추가하지 않는다.

## 3. ble-advertiser 인코딩 규약 준수

- 데이터 추출은 [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser)의 **실제 인코딩
  코드**(`AdvertisePacketBuilder.makeMinimalUuid`)를 따른다. 파싱 규칙은 두 단계로 고정한다:
  1. **Literal Segments**: UUID `8-4-4-4-12` 형식에서
     - 앞 3개 세그먼트(16자리) = **카드번호**
     - 세그먼트 4가 `0000`이고 세그먼트 5가 `00805f9b`로 끝나면 → 세그먼트 5의 앞 4자리 =
       **전화번호 뒤 4자리** (ble-advertiser / Android)
     - 세그먼트 4가 `0000`이 아니면 → 세그먼트 4 = **전화번호 뒤 4자리** (mcandle-ios-app / 레거시)
  2. **ASCII Fallback**: UUID 전체 hex를 ASCII로 변환 후 정규식 탐색
     (`010\d{8}` 전화번호, `\d{8,16}` 카드번호).
- **전화번호는 뒤 4자리만 송출된다.** 전체 번호를 기대하는 UI·로직을 만들지 않는다.
- 이 규약을 바꾸는 변경은 송신측 코드 확인 없이는 금지한다. 확인은 `ble-peer-analyst`
  에이전트로 수행하고, 결과를 [PEER_CONTRACT.md](PEER_CONTRACT.md)에 반영한다.

> 이력: 2026-08-23까지 이 항목은 세그먼트 1–3을 *전화번호*, 세그먼트 4를 *카드번호*로 규정하고
> 있었다. 상대 코드와 대조한 결과 두 필드가 뒤바뀐 것으로 확인되어 정정했다
> (`DECODED CARD: 0000`이 계속 찍히던 증상의 원인).

## 4. GATT 채널 선정: 고정 UUID 우선, Fallback 허용

- Write `fff1`, Read `fff2` (Service `fff0`)를 **1순위 고정 타겟**으로 한다.
  매칭은 전체 UUID 일치뿐 아니라 **`fff0` 서비스 안의 16비트 short 값**으로도 인정한다 —
  상대가 base UUID를 바꾼 빌드(`0000fff1-1234-1234-…`)를 배포한 전력이 있다.
- 고정 타겟이 없으면 속성(`write`/`write-without-response`/`read`) 기반 fallback 탐색을 하되,
  **Bluetooth SIG base(`…-0000-1000-8000-00805f9b34fb`) 특성은 전부 제외한다.**
  안드로이드 폰은 쓰기 가능한 시스템 특성(미디어 제어 `2b99`, 전화 `2bbe` 등)을 다수 노출하며,
  여기에 쓰면 `Insufficient Authentication`으로 실패한다.
- fallback 대상이 없으면 **아무 데도 쓰지 않는다.** 시스템 특성에 쓰는 것보다 안 쓰는 게 낫다.

## 5. 방어적 예외 처리 (Windows BLE 스택)

- Windows 블루투스 스택은 신뢰할 수 없다: 모든 BLE 호출은 예외 처리로 감싸고, 실패는
  사용자에게 원인과 대응(예: "Access Denied → 페어링 필요")을 안내한다.
- 좀비 연결 방지: 스캔 중지·새 연결 시작 전에 반드시 기존 연결을 명시적으로 해제한다.

## 6. 관측 가능성 (Observability)

- 모든 BLE 이벤트(스캔 발견, 디코딩 결과, GATT 탐색, 송수신, 오류)는 Activity Log에 남긴다.
- 로그는 `logs/ble_YYYYMMDD_HHMMSS.txt` 형식으로 로컬 저장 가능해야 한다.

## 7. Flet 버전 호환성

- Flet 0.80.x 기준으로 작성한다. 색상·아이콘은 버전 간 호환성을 위해 **문자열 리터럴**을 우선 사용한다.
- 특정 Flet 버전에서 불안정한 컨트롤(예: `FilePicker`)에 의존하지 않는다.

## 8. 문서 동기화

- 동작이 바뀌는 변경은 `CHANGELOG.md`에 기록한다.
- 설계가 바뀌는 변경은 `DESIGN.md`를 갱신한다.
- 새 기능은 코드보다 먼저 `specs/NNN-*/` (spec → plan → tasks)로 정의한다.
