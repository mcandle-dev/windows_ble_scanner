# PEER CONTRACT — ble-advertiser (Android)

상대측(광고 장치)의 **관측된 계약**을 고정한 스냅샷. 이 리포의 코드는 이 문서를 전제로 동작한다.

- **대상**: `mcandle-dev/ble-advertiser` (`com.mcandle.bleapp`)
- **기준 커밋**: `0035a76` (2026-01-18, "Implement multi-step payment flow and fix BLE race condition")
- **최종 검증**: 2026-08-23
- **갱신 방법**: `ble-peer-analyst` 에이전트 실행 (아래 §6)

> ⚠️ 이 문서는 **상대 리포를 읽어서 도출한 것**이며, 상대와 합의된 규격서가 아니다.
> 상대가 바뀌면 예고 없이 깨진다 — 그래서 커밋을 고정하고 drift를 감시한다.

## 1. 광고 (Advertising)

`AdvertisePacketBuilder.kt`. 모드는 `MINIMAL`(기본)과 `DATA` 두 가지.

### MINIMAL 모드 — Service UUID에 데이터 임베딩

```
UUID = {카드[0:8]}-{카드[8:12]}-{카드[12:16]}-0000-{전화뒤4자리}00805F9B
         └──────────── 카드번호 16자리 ────────────┘  패딩   └ 전화 ┘ └ 고정 ┘
```

예: 카드 `1234567812345678`, 전화 뒤 4자리 `1234`
→ `12345678-1234-5678-0000-123400805f9b`

| 세그먼트 | 내용 |
|---|---|
| 1–3 (16자리) | **카드번호** |
| 4 (4자리) | `0000` 고정 패딩 |
| 5 앞 4자리 | **전화번호 뒤 4자리** |
| 5 뒤 8자리 | `00805F9B` 고정값 |

> ✅ **2026-08-23 정합됨**: 이전까지 `decode_uuid_data`는 세그먼트 1–3을 *전화번호*로,
> 세그먼트 4를 *카드번호*로 읽어 두 필드가 뒤바뀌어 있었다 (로그의 `DECODED CARD: 0000`이
> 그 증상). 위 배치에 맞춰 `main.py`와 constitution §3을 정정했다.

### DATA 모드

Service Data (`0000FE10-…`)에 `카드번호+전화뒤4자리`를 ASCII 또는 BCD로 실어 보냄.
현행 `main.py`는 Service Data를 파싱하지 않으므로 이 모드는 미지원.

### Scan Response

`0000FFF0-…`(GATT 서비스 UUID)와 기기 이름을 실어 보냄. 기기 이름 기본값은 설정에서 지정.

## 2. GATT 서비스

`GattServiceConfig.kt`

| 항목 | UUID | 속성 |
|---|---|---|
| Service | `0000fff0-0000-1000-8000-00805f9b34fb` | primary |
| Write (Scanner→Store) | `0000fff1-0000-1000-8000-00805f9b34fb` | WRITE, WRITE_NO_RESPONSE / PERMISSION_WRITE |
| Read/Notify (Store→Scanner) | `0000fff2-0000-1000-8000-00805f9b34fb` | READ, NOTIFY / PERMISSION_READ |

본딩·암호화 요구 없음 (`PERMISSION_WRITE`/`PERMISSION_READ` 평문).

## 3. 명령 프로토콜 (fff1에 write)

`GattServerManager.onCharacteristicWriteRequest`. 대소문자 무시, `trim()` 후 비교.

| 페이로드 | 동작 | 응답 |
|---|---|---|
| `AT+CONNECT` | 초기 타이머 취소 → 연결 타이머(60초) 시작, UI "Connect" | `GATT_SUCCESS` + fff2에 `{"status":"success","message":"Connected"}` |
| `AT+DISCONNECT` | 타이머 전부 취소 → 1초 후 GATT 서버 종료 | `GATT_SUCCESS` + `…"Disconnected"` |
| `order_id=finish` 또는 `finish` | 결제 완료 화면 전환 | — |
| 그 외 비어있지 않은 문자열 | `order_id=` 접두사 제거 후 주문 ID로 사용 → **GATT 서버 즉시 종료** | `GATT_SUCCESS` + `…"Order received"` |
| 빈 문자열 | 파싱 실패 | `GATT_FAILURE` + `…"Data is empty"` |
| fff1 이외 특성 | 거부 | `GATT_FAILURE` |

- 페이로드는 UTF-8. `OrderDataParser`는 **비어있지 않으면 무엇이든 통과**시킨다.
- 응답 JSON은 fff2에 적재되며, Scanner가 **직접 Read** 해야 받는다 (Notify 미발송).

## 4. GATT 서버 수명 (가장 중요)

`CardFragment.kt`. 서버가 내려가는 지점이 **3곳**이며, Windows는 GATT DB를 캐싱하므로
서버가 내려가도 UI에는 연결·채널이 남는다.

| # | 트리거 | 위치 |
|---|---|---|
| 1 | "결제 시작" 탭 후 **60초** 경과 | `scanTimer.onFinish` (L482) |
| 2 | `AT+CONNECT` 수신 후 **60초** 경과 | `connectedTimer.onFinish` (L504) |
| 3 | **주문 1건 수신 즉시** | `onOrderReceived` (L242) |

추가로 `onClientDisconnected`에서 `isConnected`(= AT+CONNECT를 받은 상태)면 즉시 정리한다.

**따라서 한 번의 광고 세션에 주문은 1건만 전송 가능하다.** 연속 전송하려면 상대에서
"결제 시작"을 다시 눌러야 한다.

## 5. 이쪽(Scanner)이 지켜야 할 순서

```
1. 스캔 → mcandle 발견
2. Connect
3. fff1에 "AT+CONNECT" write        ← 필수. 안 보내면 60초 뒤 서버가 내려감
4. fff2 read → {"status":"success"} 확인
5. fff1에 주문 ID write             ← 이 시점에 상대 서버가 종료됨
6. fff2 read → 결과 확인 (선택)
```

## 6. Drift 감시

상대가 바뀌면 이 문서가 먼저 틀린다. 다음으로 재검증한다:

```
ble-peer-analyst 에이전트 실행 → 이 문서와 상대 소스를 대조 → 차이를 보고
```

소스 위치: 로컬 `D:\dev\mcandle\ble-advertiser`, 없으면
`https://github.com/mcandle-dev/ble-advertiser` 클론.

### 변경 이력 (상대측)

| 커밋 | 날짜 | 이쪽에 미친 영향 |
|---|---|---|
| `0035a76` | 2026-01-18 | 다단계 결제 플로우 도입. 주문 수신 즉시 서버 종료(§4-3) |
| `972ee88` | 2025-12-08 | `AT+CONNECT` + 60초 타임아웃 도입 — **Send 실패의 근원** |
| `792daf4` | 2025-11-10 | iBeacon 스캔 → GATT 서버 아키텍처로 전환 (v2.0) |
