# DESIGN — windows_ble_scanner

> **한 줄 설명**: mcandle 광고 장치(Android/iOS)가 Service UUID에 임베딩해 송출하는
> 전화번호·카드번호를 Windows에서 실시간 스캔·디코딩하고, GATT 연결로 주문 정보를 읽고
> 주문 번호를 써 보내는 단일 파일 Flet 데스크톱 앱 — 결제 단말기(Scanner) 역할.

이 문서는 **현행 시스템의 실제 구조**를 기술한다. 원칙은 [constitution.md](constitution.md),
기능 이력은 [CHANGELOG.md](CHANGELOG.md), 진행 단위는 [specs/](specs/) 참조.

## 1. 시스템 경계

```
┌──────────────────────┐   BLE Advertising    ┌──────────────────────────────┐
│  광고 장치 (Peripheral) │ ───────────────────► │  windows_ble_scanner (본 리포) │
│                       │   Service UUID에      │  Windows Central/Scanner      │
│  주: ble-advertiser    │   전화번호·카드번호 임베딩│                              │
│      (Android, 현행)   │                      │  main.py (Flet + Bleak)      │
│  참고: mcandle-ios-app │ ◄──────────────────► │                              │
│      (zip 동봉)        │   GATT Read/Write     │                              │
└──────────────────────┘   + AT+CONNECT        └──────────────────────────────┘
```

- 본 리포는 **수신(Central/Scanner) 측**만 구현한다.
- **현행 상대는 Android 앱 `mcandle-dev/ble-advertiser`** (`com.mcandle.bleapp`)이며,
  프로토콜 기준 문서는 그 리포의 `GATT_SEQUENCE_DIAGRAM.md`다. 제약은 §5 참조.
- 리포에 동봉된 `mcandle-ios-app.zip`은 **과거 iOS 참조 구현**이다 (별개 코드베이스).
  현재 검증 대상이 아니므로, 동작 차이가 보이면 Android 쪽을 기준으로 삼을 것.
- 실행 환경: Windows + Bluetooth 하드웨어 (Bleak → WinRT 백엔드).

## 2. 구성 요소 (main.py 단일 파일)

`BLEScannerApp` 클래스 하나가 상태·UI·BLE 로직을 모두 소유한다.

| 영역 | 메서드 | 역할 |
|---|---|---|
| 스캔 루프 | `run_scan` | `BleakScanner.discover(timeout=5, return_adv=True)`를 1초 간격 무한 루프로 반복. 광고 내용(이름+카드+전화)으로 중복 MAC을 합친 뒤 테이블 갱신 |
| 디코딩 | `decode_uuid_data` | Service UUID → 전화번호/카드번호 (constitution §3의 2단계 규칙) |
| 연결 | `connect_device` | 스캔 자동 중지 → 기존 연결 해제 → 연결 → GATT 서비스 전수 탐색 → Read/Write 채널 선정 (constitution §4) → 초기 Read로 Order Information 표시 → `AT+CONNECT` 핸드셰이크 |
| 핸드셰이크 | `send_handshake` | 연결 직후 `AT+CONNECT` 전송. 상대(ble-advertiser)의 대기 타이머를 취소시킴 |
| 해제 | `disconnect_current_device` | 좀비 연결 방지용 명시적 disconnect |
| 해제 감지 | `on_device_disconnected` | Bleak 콜백. 상대가 링크를 끊으면 채널 표시 초기화 + Send 비활성화 |
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
- 좌측 두 패널(Detected Devices 3 : Connection Information 2)과 우측 로그 모두 `expand` 기반이라
  창 크기·분할 위치 변경에 함께 대응한다. 장치 테이블은 좌우 스크롤을 가진다.

## 4. 핵심 흐름

1. **스캔**: Start Scan 시 이전 결과를 비운 뒤 시작 → 루프마다 발견 장치를 필터링
   → UUID 디코딩 → **광고 내용 기준 중복 제거**(MAC 회전 대응, 최강 RSSI 채택)
   → 테이블 재구성 → 로그 기록.
2. **연결**: Connect 클릭 → 스캔 중지·기존 연결 해제 → GATT 전수 탐색을 로그로 출력
   → 고정 UUID 매칭(Fixed) 또는 fallback으로 Read/Write 채널 확정 → 확정된 채널에서
   초기 Read → Order Information 표시 → `AT+CONNECT` 핸드셰이크 전송.
3. **송신**: Send → 전제 조건 검사(미충족 시 사유를 로그에 기록) → 스위치 값에 따라
   With/Without Response 결정 → 실패 시 원인 안내(Access Denied → 페어링 필요,
   연결 종료 → 상대 GATT 서버 타임아웃 안내).
4. **해제 감지**: 상대가 링크를 끊으면 Bleak 콜백이 채널 표시를 초기화하고 Send를 비활성화.

## 5. 상대측(Peer) 제약 — ble-advertiser (Android)

> 전체 계약(광고 인코딩·명령 프로토콜·응답 스키마)은 [PEER_CONTRACT.md](PEER_CONTRACT.md) 참조.
> 상대 변경 여부는 `ble-peer-analyst` 에이전트로 재검증한다.

송신측 `mcandle-dev/ble-advertiser`의 GATT 서버는 **수명이 짧다**. 이 앱의 동작을 이해하려면
반드시 함께 봐야 한다 (`CardFragment.kt`):

- "결제 시작" 탭 후 **60초** 카운트다운 → 만료 시 `stopAdvertiseAndGatt()`로 GATT 서버 종료.
- `AT+CONNECT` 수신 시 위 타이머를 취소하고 **연결 타이머 60초**를 새로 시작.
- **주문 1건을 수신하면 즉시** GATT 서버를 종료하고 결제 상세 화면으로 전환.
  → 한 번 연결에 한 번만 전송 가능. 연속 전송하려면 상대에서 다시 광고를 시작해야 한다.

Windows는 GATT 서비스 DB를 캐싱하므로, 상대가 서버를 내려도 채널 정보가 UI에 남는다.
이 때문에 `disconnected_callback` 등록이 필수다.

## 6. 알려진 제약 / 기술 부채

- 스캔 루프가 `discover()` 폴링 방식이라 갱신 주기가 ~6초(타임아웃 5s + sleep 1s).
- 자동 재연결 없음 (해제 감지까지만 구현됨).
- 테스트 코드 없음. 실기기(Windows BT + Android/iOS 광고 장치) 수동 검증에 의존.

## 7. 저장소 구조

```
main.py            # 애플리케이션 전체 (UI + BLE)
requirements.txt   # 고정 버전 (bleak 2.1.1, flet 0.80.2, winrt-*)
requirements.md    # 원 요구 정의서 (역사적 문서)
constitution.md    # 불변 원칙
DESIGN.md          # 이 문서
CLAUDE.md          # AI 에이전트 작업 지침
PEER_CONTRACT.md   # 상대측(ble-advertiser) 계약 스냅샷
KICKOFF_PROMPT.md  # 새 세션 시작 프롬프트
specs/NNN-*/       # 기능 단위 spec/plan/tasks
logs/              # BLE 세션 로그 + 작업 일지
mcandle-ios-app.zip# 송신측 iOS 참조 구현
```
