# Plan 001 — BLE Scanner MVP

- **상태**: ✅ 완료 (소급 기록)
- **spec**: [spec.md](spec.md)

## 1. 기술 선택 (How)

| 결정 | 선택 | 근거 |
|---|---|---|
| BLE 라이브러리 | `bleak` | Windows WinRT 백엔드를 가진 사실상 표준 asyncio BLE 클라이언트 |
| UI | `flet` | Python 단독으로 데스크톱 GUI 구성, asyncio와 자연스럽게 결합 |
| 광고 데이터 접근 | `BleakScanner.discover(return_adv=True)` | 연결 없이 `service_uuids`/`rssi` 접근 (BLEDevice 속성 접근은 deprecated) |
| 구조 | 단일 클래스 `BLEScannerApp` in `main.py` | MVP 단순성 (constitution 제4조) |

## 2. 아키텍처 개요

- `BLEScannerApp`이 상태·UI·BLE 로직을 소유. 스캔은 `asyncio.create_task`로 백그라운드 루프,
  버튼 핸들러의 코루틴은 `page.run_task()`로 실행.
- 디코딩은 순수 함수형 메서드 `decode_uuid_data(uuids) -> (phone, card)`로 격리.
- GATT 채널 선정은 2단계 우선순위: 고정 UUID(`fff1`/`fff2`) 정합 → 속성 기반 fallback
  (시스템 특성 제외).

## 3. 주요 리스크와 대응 (구현 중 실제 발생분 포함)

| 리스크 | 대응 |
|---|---|
| Flet 0.80.x 파괴적 변경 (아이콘/색상/`FilePicker`) | 문자열 리터럴 스타일, `FilePicker` 제거 후 직접 파일 I/O |
| 시스템 GATT 특성 접근 시 Access Denied | 시스템 특성 블랙리스트로 대상 제외 |
| iOS 수신 누락 (Write Without Response) | With Response 기본값 + UI 스위치로 오버라이드 |
| 좀비 연결로 재연결 실패 | 스캔 중지·신규 연결 시 명시적 disconnect |
| UI 세션 파괴 후 update 예외 | `page.session` 확인 및 try/except 가드 |

## 4. 검증 방법

- 실기기 수동 테스트: ble-advertiser 방식 iOS 앱(광고 송출)과 페어 테스트.
- 스캔 로그(`logs/ble_*.txt`)로 디코딩 결과 검증.
