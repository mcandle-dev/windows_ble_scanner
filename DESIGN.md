# DESIGN — windows_ble_scanner

> **한 줄 설명**: iOS 광고 장치(mcandle)가 Service UUID에 임베딩해 송출하는 전화번호·카드번호를
> Windows에서 실시간 스캔·디코딩하고, GATT 연결로 주문 정보를 읽고 메시지를 써 보내는
> 단일 파일 Flet 데스크톱 앱.

이 문서는 **현행 시스템의 실제 구조**를 기술한다. 원칙은 [constitution.md](constitution.md),
기능 이력은 [CHANGELOG.md](CHANGELOG.md), 진행 단위는 [specs/](specs/) 참조.

## 1. 시스템 경계

```
┌─────────────────────┐   BLE Advertising    ┌──────────────────────────────┐
│  iOS 앱 (Peripheral) │ ───────────────────► │  windows_ble_scanner (본 리포) │
│  mcandle-ios-app     │   Service UUID에      │  Windows Central/Client       │
│  (참조: zip 동봉,     │   전화번호·카드번호 임베딩│                              │
│   ble-advertiser 방식)│                      │  main.py (Flet + Bleak)      │
│                      │ ◄──────────────────► │                              │
└─────────────────────┘   GATT Read/Write     └──────────────────────────────┘
```

- 본 리포는 **수신(Central) 측**만 구현한다. 송신 측 인코딩 규약은 ble-advertiser /
  `mcandle-ios-app.zip` (BLEPeripheral.swift)이 기준이다.
- 실행 환경: Windows + Bluetooth 하드웨어 (Bleak → WinRT 백엔드).

## 2. 구성 요소 (main.py 단일 파일)

`BLEScannerApp` 클래스 하나가 상태·UI·BLE 로직을 모두 소유한다.

| 영역 | 메서드 | 역할 |
|---|---|---|
| 스캔 루프 | `run_scan` | `BleakScanner.discover(timeout=5, return_adv=True)`를 1초 간격 무한 루프로 반복, 장치 테이블 갱신 |
| 디코딩 | `decode_uuid_data` | Service UUID → 전화번호/카드번호 (constitution §3의 2단계 규칙) |
| 연결 | `connect_device` | 스캔 자동 중지 → 기존 연결 해제 → 연결 → GATT 서비스 전수 탐색 → Read/Write 채널 선정 (constitution §4) → 초기 Read로 Order Information 표시 |
| 해제 | `disconnect_current_device` | 좀비 연결 방지용 명시적 disconnect |
| 송신 | `send_data` | UTF-8 인코딩 후 `write_gatt_char`; Response 여부는 UI 스위치로 사용자 제어 |
| 로깅 | `log_message`, `save_logs_direct` | UI 로그(최대 100줄 표시/1000줄 버퍼) + `logs/` 파일 저장 |

### 주요 상태

- `devices: dict[address → {device, phone, card, rssi}]`
- `connected_client: BleakClient | None` — 동시 연결은 1대만
- `target_write_char` — 송신 대상 특성 (연결 시 선정)
- `is_scanning` / `scanning_task` — 스캔 루프 제어

### 고정 GATT 상수

```python
TARGET_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
TARGET_WRITE_UUID   = "0000fff1-0000-1000-8000-00805f9b34fb"
TARGET_READ_UUID    = "0000fff2-0000-1000-8000-00805f9b34fb"
```

## 3. UI 레이아웃 (Flet, Dark 모드)

```
┌ Header: 타이틀 | 이름 필터(기본 "mcan", like-search) | Start/Stop Scan ┐
├──────────────────────────────┬─┬──────────────────────────────────┤
│ Detected Devices (DataTable) │d│ Activity Logs (ListView)          │
│  Name(MAC)|Phone|Card|RSSI|  │r│  + Save 버튼 → logs/ble_*.txt     │
│  [Connect]                   │a│                                   │
│ Connection Information       │g│                                   │
│  Order Info / Read·Write 채널 │ │                                   │
│  Write Response 스위치        │ │                                   │
│  메시지 입력 + [Send]          │ │                                   │
├──────────────────────────────┴─┴──────────────────────────────────┤
│ Status bar                                                        │
└───────────────────────────────────────────────────────────────────┘
```

- 좌우 50:50, `GestureDetector` 드래그로 좌측 폭 조절(300–1200px).

## 4. 핵심 흐름

1. **스캔**: 루프마다 발견 장치를 필터링 → UUID 디코딩 → 테이블 재구성 → 로그 기록.
2. **연결**: Connect 클릭 → 스캔 중지·기존 연결 해제 → GATT 전수 탐색을 로그로 출력
   → 고정 UUID 매칭(Fixed) 또는 fallback으로 Read/Write 채널 확정 → 초기 Read 결과를
   Order Information에 표시.
3. **송신**: Send → 스위치 값에 따라 With/Without Response 결정 → 실패 시 원인 안내
   (Access Denied → 페어링 필요).

## 5. 알려진 제약 / 기술 부채

- 스캔 루프가 `discover()` 폴링 방식이라 갱신 주기가 ~6초(타임아웃 5s + sleep 1s).
- 연결 상태 관리가 단순함(재연결·연결 유실 감지 없음) — work log에 개선 목표로 기록됨.
- 테스트 코드 없음. 실기기(Windows BT + iOS 광고 장치) 수동 검증에 의존.
- `decode_uuid_data`의 literal 판정 휴리스틱(`010`/`1234` prefix)은 데모 데이터에 맞춘 것.

## 6. 저장소 구조

```
main.py            # 애플리케이션 전체 (UI + BLE)
requirements.txt   # 고정 버전 (bleak 2.1.1, flet 0.80.2, winrt-*)
requirements.md    # 원 요구 정의서 (역사적 문서)
constitution.md    # 불변 원칙
DESIGN.md          # 이 문서
CLAUDE.md          # AI 에이전트 작업 지침
KICKOFF_PROMPT.md  # 새 세션 시작 프롬프트
specs/NNN-*/       # 기능 단위 spec/plan/tasks
logs/              # BLE 세션 로그 + 작업 일지
mcandle-ios-app.zip# 송신측 iOS 참조 구현
```
