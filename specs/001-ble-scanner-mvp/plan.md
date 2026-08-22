# Plan 001 — BLE Scanner MVP (소급 기록)

spec: [spec.md](spec.md) · 실제 구현 결과는 [../../DESIGN.md](../../DESIGN.md)에 반영됨

## 기술 선택

| 선택 | 근거 |
|---|---|
| Python 3.10+ | 빠른 MVP 개발, Windows BLE 라이브러리 성숙도 |
| Bleak 2.1.1 | Windows(WinRT) 비동기 BLE 표준 라이브러리. `discover(return_adv=True)`로 무연결 광고 데이터 접근 |
| Flet 0.80.2 | Python 단독으로 데스크톱 GUI + asyncio 통합(`page.run_task`) |
| 단일 파일 main.py | MVP 규모에서 모듈 분리 오버헤드 회피 (constitution §2) |

## 구현 접근

1. **스캔**: `BleakScanner.discover()` 폴링 루프 (1초 간격). 콜백형 스캐너 대신 폴링을 택한 이유:
   Windows에서 advertisement 데이터(`service_uuids`, `rssi`) 접근이 `return_adv=True` 방식이 가장 안정적.
2. **디코딩**: 순수 함수 `decode_uuid_data(uuids) -> (phone, card)`. Literal Hex → ASCII fallback 순.
3. **연결**: 연결 시 GATT 전수 탐색을 하며 채널 선정과 로깅을 동시에 수행.
   고정 UUID 매칭이 fallback보다 항상 우선.
4. **송신**: 특성의 지원 속성 자동 판단 대신 **사용자 스위치**로 Response 여부를 제어
   (iOS 수신 신뢰성 문제로 With Response를 기본값으로 결정 — 커밋 `a0b91bd`).
5. **UI**: Flet 컨트롤 트리 1회 구성 후 `page.update()`로 갱신. 버전 호환을 위해 색상/아이콘은
   문자열 리터럴 사용.

## 리스크와 대응 (구현 중 실제 발생분 포함)

| 리스크 | 대응 |
|---|---|
| Flet 0.80.x breaking changes (`FilePicker` 불안정, 아이콘 경로 변경) | FilePicker 제거, `logs/` 직접 저장; 문자열 스타일링 |
| 시스템 GATT 특성 접근 시 Access Denied | 시스템 특성(2a00 등) 블랙리스트 제외 |
| 좀비 연결로 재연결 실패 | 스캔 중지/연결 시작 시 명시적 disconnect |
| Write Without Response를 iOS가 유실 | With Response 기본값 + 사용자 오버라이드 스위치 |

## 검증 방법

- 자동 테스트 없음(실기기 의존). Windows PC + mcandle iOS 앱으로 수동 시나리오 검증,
  결과는 `logs/ble_*.txt`로 보존.
