# DESIGN — windows_ble_scanner

> **제품 한 줄 설명**: Windows에서 주변 BLE 광고를 스캔해 Service UUID에 임베딩된
> 전화번호·카드번호를 실시간 디코딩하고, 선택한 장치와 GATT Read/Write로 통신하는
> Flet 기반 데스크톱 앱.

이 문서는 **현행 시스템의 실체**를 기록하는 설계도다. 구현(`main.py`)이 바뀌면 이 문서를 함께 갱신한다.
불변 원칙은 [constitution.md](constitution.md), 진행 중 작업은 [specs/](specs/) 참조.

## 1. 시스템 컨텍스트

```
┌─────────────────────┐   BLE Advertisement    ┌──────────────────────────┐
│  iOS Peripheral 앱   │   (Service UUID에      │  windows_ble_scanner     │
│  (mcandle-ios-app,  │ ──전화번호/카드번호 임베딩──▶ │  (이 리포, Central 역할)  │
│  ble-advertiser 방식)│                        │  Windows + Bleak + Flet  │
│                     │ ◀──── GATT Read/Write ──▶ │                          │
└─────────────────────┘                        └──────────────────────────┘
```

- 상대편 장치는 [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser) 인코딩
  방식으로 광고를 송출하는 BLE Peripheral이다. 리포에 동봉된 `mcandle-ios-app.zip`은
  그 iOS 구현(CoreBluetooth Peripheral, 결제 정보 광고)의 참조 스냅샷이다.
- 이 앱은 Central 역할만 수행한다: 스캔 → 디코딩 → 연결 → GATT Read/Write.

## 2. 실행 구조

- **단일 프로세스, 단일 파일**: `main.py`의 `BLEScannerApp` 클래스가 UI와 BLE 로직을 모두 소유한다.
- **런타임**: Python 3.10+, Windows 전용(WinRT 기반 `bleak` 백엔드). Linux/CI에서는 BLE 동작 불가.
- **진입점**: `ft.run(main)` → `BLEScannerApp(page)` 생성 → `setup_ui()`.

### 주요 상태 (BLEScannerApp 인스턴스 변수)

| 상태 | 의미 |
|---|---|
| `devices` | 스캔 결과 캐시 `{address: {device, phone, card, rssi}}` |
| `connected_client` | 현재 연결된 `BleakClient` (없으면 `None`) |
| `target_write_char` | 선택된 Write 대상 Characteristic |
| `is_scanning` / `scanning_task` | 스캔 루프 플래그와 asyncio task |
| `all_logs` | 저장용 로그 버퍼 (최대 1000줄, UI는 100줄) |
| `write_response_switch` | Write 시 Response 사용 여부 (기본 True) |

## 3. 핵심 흐름

### 3.1 스캔 루프 (`run_scan`)

1. `BleakScanner.discover(timeout=5.0, return_adv=True)`로 주변 장치와 광고 데이터를 획득.
   - `return_adv=True`가 필수: 연결 없이 `service_uuids`, `rssi`에 접근하기 위함.
2. 장치 이름 필터(`filter_input`, 대소문자 무시 like 검색, 기본값 `"mcan"`) 적용.
3. 각 장치의 `service_uuids`를 `decode_uuid_data()`로 디코딩.
4. DataTable 갱신 + 로그 기록 후 1초 대기, `is_scanning`이 참인 동안 반복.

### 3.2 디코딩 (`decode_uuid_data`) — constitution 제6조

- **Rule A (Literal Hex)**: UUID 5분할 시 세그먼트 1~3 결합(16자리)=전화번호,
  세그먼트 4(4자리)=카드번호. 전화번호가 `010` 또는 `1234`로 시작할 때만 채택.
- **Rule B (ASCII Fallback)**: 하이픈 제거한 hex를 ASCII 변환 후
  `010\d{8}`(전화번호), `\d{8,16}`(카드번호) 정규식 탐색.

### 3.3 연결과 GATT 탐색 (`connect_device`)

1. 스캔 중이면 자동 중지, 기존 연결은 `disconnect_current_device()`로 명시적 해제(좀비 연결 방지).
2. `BleakClient(address).connect()` 후 `client.services` 순회, 모든 Service/Char와 속성 로깅.
3. 채널 선택 우선순위:
   - **Priority 1**: 고정 UUID 정합 — Write `0000fff1-…`, Read `0000fff2-…` (`TARGET_*_UUID` 상수).
   - **Priority 2**: 속성 기반 fallback — `write`/`write-without-response` 보유 특성,
     `read` 보유 특성. 단, 시스템 특성(`2a00`,`2a01`,`2a05`,`2b29`,`2b2a`)은 제외
     (Access Denied 회피).
4. Read 특성에서 초기 데이터를 읽어 UTF-8 디코딩 후 'Order Information'에 표시.

### 3.4 데이터 전송 (`send_data`)

- 입력 텍스트를 UTF-8 인코딩해 `write_gatt_char(uuid, msg, response=<스위치 값>)`으로 전송.
- Response 여부는 UI 스위치("Write Channel Response")가 결정한다.
  iOS 수신 신뢰성 문제로 **With Response가 기본값**이다 (commit a0b91bd).
- `Access Denied` 발생 시 페어링/본딩 필요 안내를 상태줄에 표시.

## 4. UI 레이아웃

```
┌──────────────────────────────────────────────────────────────┐
│ Header: 타이틀 | 이름 필터 | Start/Stop Scan (파랑/빨강 토글)     │
├───────────────────────────┬──╢드래그 디바이더╟──────────────────┤
│ Detected Devices          │  │ Activity Logs        [저장 버튼] │
│  (DataTable: Name/Phone/  │  │  (ListView, 검정 배경,          │
│   Card/RSSI/Connect)      │  │   타임스탬프 로그, auto-scroll)  │
├───────────────────────────┤  │                                │
│ Connection Information    │  │  저장 → logs/ble_*.txt         │
│  + Write Response 스위치   │  │                                │
│  Order Info / Read·Write  │  │                                │
│  채널 표시 / 메시지 입력+Send │  │                                │
├───────────────────────────┴──┴────────────────────────────────┤
│ Footer: Status 텍스트                                          │
└──────────────────────────────────────────────────────────────┘
```

- 좌우 50:50 분할, `GestureDetector` 드래그로 좌측 폭 300~1200px 조절 가능.
- Dark 테마 고정, 창 최대화 시작.

## 5. 기술 스택과 제약

| 구성 | 선택 | 비고 |
|---|---|---|
| 언어 | Python 3.10+ | |
| BLE | bleak 2.1.1 | WinRT 백엔드, asyncio 기반 |
| UI | flet 0.80.2 (고정) | 0.80.x 파괴적 변경 대응: 문자열 색상/아이콘, `ft.run()` 사용 |
| 로그 저장 | 직접 파일 I/O | `FilePicker`는 0.80.x에서 불안정하여 제거됨 |

상세 배경은 `TECHNICAL_STACK.md` 참조.

## 6. 알려진 한계 (현행)

- 연결 유지 관리가 단순함: 재연결·연결 끊김 감지(disconnect callback)·재시도 없음
  → [specs/002-gatt-connection-stability](specs/002-gatt-connection-stability/) 진행 중.
- Notify/Indicate 미지원 (Read는 연결 시 1회).
- 페어링/본딩 흐름은 안내만 하고 자동 처리하지 않음.
- 스캔 루프가 매 사이클 전체 리스트를 다시 그림 (증분 갱신 아님).
