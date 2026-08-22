# Spec 001 — BLE Scanner MVP

- **상태**: ✅ 완료 (소급 기록 — 2026-01-18 ~ 2026-01-25 구현분을 SDD 전환 시점에 문서화)
- **관련**: [plan.md](plan.md) · [tasks.md](tasks.md) · [DESIGN.md](../../DESIGN.md)

## 1. 배경 및 목적 (Why)

[ble-advertiser](https://github.com/mcandle-dev/ble-advertiser) 방식으로 Service UUID에
결제 정보(전화번호·카드번호)를 임베딩해 광고하는 BLE Peripheral(iOS 앱)을 검증하기 위한
Windows용 카운터파트가 필요하다. 광고 수신·디코딩·GATT 양방향 통신을 한 화면에서
확인할 수 있는 MVP 도구를 만든다.

## 2. 사용자 시나리오

1. 운영자가 앱을 실행하고 **Start Scan**을 누르면 주변 BLE 장치가 표에 나타난다.
2. 장치 이름 필터(예: `mcan`)로 대상 장치만 좁혀 본다.
3. 대상 장치 행에서 광고에 임베딩된 **전화번호·카드번호가 자동 디코딩**되어 보인다.
4. **Connect**를 누르면 GATT 서비스가 탐색되고, 읽기 채널에서 주문 정보(Order Information)를 읽어 표시한다.
5. 메시지를 입력하고 **Send**를 누르면 쓰기 채널로 장치에 전송된다.
6. 전 과정이 Activity Logs에 기록되고, 저장 버튼으로 `logs/`에 파일 백업된다.

## 3. 기능 요구사항 (What)

| ID | 요구사항 | 수용 기준 |
|---|---|---|
| FR-1 | 실시간 BLE 스캔 | 주기적 재스캔으로 장치 목록·RSSI 갱신, Start/Stop 토글 |
| FR-2 | UUID 데이터 디코딩 | Literal Hex(세그먼트 1-3=전화, 4=카드) 우선, ASCII 정규식 fallback |
| FR-3 | 장치 이름 필터 | 대소문자 무시 like 검색, 입력 즉시 반영 |
| FR-4 | GATT 연결·탐색 | 연결 후 전체 Service/Char와 속성을 로깅, 채널 자동 선정 |
| FR-5 | 데이터 읽기 | Read 특성에서 UTF-8 디코딩하여 Order Information 표시 |
| FR-6 | 데이터 쓰기 | Write/Write-Without-Response 지원, Response 여부 UI에서 선택 |
| FR-7 | 로그 | 타임스탬프 로그 표시 + `logs/ble_YYYYMMDD_HHMMSS.txt` 저장 |
| FR-8 | UI | Dark 테마, 50:50 분할, 드래그로 크기 조절 |

## 4. 비기능 요구사항

- UI 프리징 금지 — 모든 BLE 작업 비동기 (constitution 제1조).
- BLE 오류로 앱이 죽지 않을 것 (constitution 제2조).
- 단일 파일 구조 유지 (constitution 제4조).

## 5. 범위 제외 (Out of Scope)

- Notify/Indicate 구독, 자동 재연결, 페어링 자동화 → Spec 002 이후로 이관.
- 광고 송출(Peripheral 역할), 다중 동시 연결.
