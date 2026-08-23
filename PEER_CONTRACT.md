# PEER CONTRACT — ble-advertiser (Android)

상대측(광고 장치)의 **관측된 계약**을 고정한 스냅샷. 이 리포의 코드는 이 문서를 전제로 동작한다.

- **대상**: `mcandle-dev/ble-advertiser` (`com.mcandle.bleapp`)
- **기준 커밋**: `0035a76` (2026-01-18, "Implement multi-step payment flow and fix BLE race condition")
- **최종 검증**: 2026-08-23
- **갱신 방법**: `ble-peer-analyst` 에이전트 실행 (아래 §6)

> ⚠️ 이 문서는 **상대 리포를 읽어서 도출한 것**이며, 상대와 합의된 규격서가 아니다.
> 상대가 바뀌면 예고 없이 깨진다 — 그래서 커밋을 고정하고 drift를 감시한다.

## 1. 광고 (Advertising)

`AdvertisePacketBuilder.kt`. 모드는 설정에서 `MINIMAL`(기본)과 `DATA` 중 선택.

> **MINIMAL이 운영 모드다.** `DATA` 모드는 페이로드를 Service Data에 싣는데 iOS Central이
> 이를 읽지 못해 채택하지 않았다. 따라서 이쪽이 Service Data를 파싱하지 않는 것은 결함이 아니라
> 의도된 것이다 — "DATA 모드 미지원"을 갭으로 보고 구현하지 말 것.

### MINIMAL 모드 — Service UUID에 데이터 임베딩

카드번호가 세그먼트 1–3을 채우고, **전화번호는 뒤 4자리만** 실린다. 다만 그 4자리의 위치가
빌드마다 다르므로 **두 배치를 모두 수용해야 한다.**

**배치 A — GitHub HEAD (`0035a76`)**
```
{카드[0:8]}-{카드[8:12]}-{카드[12:16]}-0000-{전화4}00805F9B
  └────────── 카드번호 16자리 ──────────┘  패딩  └전화┘ └ 고정 ┘
예: 12345678-1234-5678-0000-123400805f9b
```

**배치 B — 2026-08-23 실기기 로그의 빌드 (레거시 iOS와 동일)**
```
{카드[0:8]}-{카드[8:12]}-{카드[12:16]}-{전화4}-00805F9B34FB
  └────────── 카드번호 16자리 ──────────┘  └전화┘  └── 고정 ──┘
예: 12345678-1234-5678-1234-00805f9b34fb
```

| 세그먼트 | 배치 A | 배치 B |
|---|---|---|
| 1–3 (16자리) | **카드번호** | **카드번호** |
| 4 (4자리) | `0000` 고정 패딩 | **전화번호 뒤 4자리** |
| 5 (12자리) | **전화4** + `00805F9B` | `00805F9B34FB` 고정 |

판별: 세그먼트 4가 `0000`이고 세그먼트 5가 `00805f9b`로 끝나면 배치 A, 그 외에는 배치 B.

> ✅ **2026-08-23 정합됨**: 이전까지 `decode_uuid_data`는 세그먼트 1–3을 *전화번호*로,
> 세그먼트 4를 *카드번호*로 읽어 두 필드가 뒤바뀌어 있었다 (로그의 `DECODED CARD: 0000`이
> 그 증상). 위 배치에 맞춰 `main.py`와 constitution §3을 정정했다.

### DATA 모드 — 미사용

Service Data (`0000FE10-…`)에 `카드번호+전화뒤4자리`를 ASCII 또는 BCD로 실어 보낸다.
**iOS Central이 Service Data를 읽지 못해 운영에서 쓰지 않는다.** 이쪽도 파싱하지 않는다.

### MAC 주소 회전

Android는 BLE 주소를 수 분마다 바꾼다(랜덤 사설 주소). **같은 폰이 여러 MAC으로 보인다.**
따라서 MAC은 기기 식별자로 쓸 수 없고, 광고 내용(이름+카드+전화)으로 식별해야 한다.
이전에 본 MAC은 회전 후 연결 불가가 되므로, 목록에서는 **최근/최강 신호의 MAC**을 쓴다.

### Scan Response

`0000FFF0-…`(GATT 서비스 UUID)와 기기 이름을 실어 보냄. 기기 이름 기본값은 설정에서 지정.

## 2. GATT 서비스

`GattServiceConfig.kt`

16비트 값은 `fff0`(Service) / `fff1`(Write) / `fff2`(Read·Notify)로 고정이며,
**base UUID는 두 가지가 병존한다.**

| base | 사용처 | 예 (Write) |
|---|---|---|
| `-1234-1234-8000-00805f9b34fb` | **현행 로컬 빌드 (의도된 변경)** | `0000fff1-1234-1234-8000-00805f9b34fb` |
| `-0000-1000-8000-00805f9b34fb` | GitHub HEAD `0035a76` (미갱신) | `0000fff1-0000-1000-8000-00805f9b34fb` |

| 항목 | 속성 |
|---|---|
| Service `fff0` | primary |
| Write `fff1` (Scanner→Store) | WRITE, WRITE_NO_RESPONSE / PERMISSION_WRITE |
| Read `fff2` (Store→Scanner) | READ, NOTIFY / PERMISSION_READ |

본딩·암호화 요구 없음 (`PERMISSION_WRITE`/`PERMISSION_READ` 평문).

> **벤더 base(`-1234-1234-`)는 의도된 설계다** (2026-08-23 사용자 확인). 표준 base로
> 되돌리자고 제안하지 말 것. GitHub HEAD가 아직 표준인 것은 로컬 변경이 푸시되지 않았기 때문이다.
> 실측 근거: `logs/ble_20260823_130656.txt`.
>
> 이쪽은 **`fff0` 서비스 내 16비트 short UUID 매칭**으로 두 base를 모두 수용한다
> (constitution §4). 어느 한쪽만 지원하도록 단순화하지 말 것.
>
> 광고의 Scan Response에는 표준 `0000fff0-0000-1000-8000-…`가 실린다 — 광고와 실제 GATT
> 서비스의 base가 다르므로, 광고에서 본 UUID로 GATT 특성을 찾으려 하면 안 된다.

### 다른 Central: POS 단말 앱 (`mcandle-dev/vpos_claude_pos`)

이 리포 외에 **POS 단말 앱도 같은 광고 장치에 붙는다.** 이쪽 변경이 그쪽을 깨뜨리지 않는지
확인이 필요할 때 참고할 것. 그 앱은 Android GATT API가 아니라 단말 벤더 SDK에 AT 명령
(`AT+MASTER_PAIR` → `AT+UUID_SCAN=1` → `AT+CONNECT` → `AT+TRX_CHAN` → `AT+SEND`)을 보낸다.

- 채널 선정이 두 갈래로 갈려 있다: `BeaconActivity.java:932`는 `uuid.equals("DECA")`,
  브랜치 `claude/fix-android-15-uuid-C148W`의 `BleConnection.java:718`은 `contains("f1ff")`.
  둘 다 `fff1`과 무관한 값이라 어느 쪽이 실제 경로인지 미확인.
- 그 앱은 주석에 표준 base를 전제로 적어두었다(`BleConnection.java:705-707`).
  단말이 `AT+UUID_SCAN` 응답에 16비트 short를 주는지 128비트 전체를 주는지에 따라
  벤더 base가 그쪽 매칭에 영향을 줄 수 있다 — **실기기 로그로만 확인 가능.**
- 쓰기 방식은 `AT+TRX_CHAN=…,1` → type=1 = With Response. 이쪽 기본값과 일치한다.

### ⚠️ fff0 서비스가 두 벌로 보인다 (원인 미확정)

2026-08-23 실기기에서 Windows 쪽 탐색 결과에 **`fff0` 서비스 블록이 두 번** 나타나
`fff1`/`fff2`가 각각 2개씩 잡혔다. 상대 앱은 서비스 하나에 write·read 채널을 등록할 뿐이라고
확인됨 — 따라서 원인은 앱 코드가 아니라 **Windows GATT 캐시에 이전 서비스 정의가 남은 것**일
가능성이 높다 (base UUID를 바꾼 빌드로 교체한 이력이 있어 캐시와 현행이 공존할 수 있다).
확정하려면 Windows에서 해당 기기의 페어링/캐시를 지우고 재탐색해봐야 한다.

이 상태에서 **UUID 문자열로 특성을 지정하면 Bleak이 실패한다**:
`Multiple Characteristics with this UUID, refer to your desired characteristic by the 'handle' attribute instead`

→ 이쪽은 **특성 객체(handle)로 지정**하고, 매칭된 것이 여럿이면 순서대로 시도한다.
UUID 문자열로 되돌리지 말 것.

### 안드로이드 폰의 시스템 특성 (fallback 금지 대상)

폰 자체가 SIG 표준 서비스를 다수 노출하며, 쓰기 가능한 것도 많다:
Generic Media Control(`1849`, 예 `2b99`), Generic Telephone Bearer(`184c`, 예 `2bbe`),
Telephony and Media Audio(`1855`). **여기에 쓰면 `Insufficient Authentication`으로 실패한다.**
fallback 탐색에서 SIG base(`…-0000-1000-8000-00805f9b34fb`) 특성은 전부 제외해야 한다.

## 3. 명령 프로토콜 (fff1에 write)

`GattServerManager.onCharacteristicWriteRequest`. 대소문자 무시, `trim()` 후 비교.

| 페이로드 | 동작 | 응답 |
|---|---|---|
| `AT+CONNECT` | 초기 타이머 취소 → 연결 타이머(60초) 시작, UI "Connect" | `GATT_SUCCESS` + fff2에 `Connected` |
| `AT+DISCONNECT` | 타이머 전부 취소 → 1초 후 GATT 서버 종료 | `GATT_SUCCESS` + fff2에 `Disconnected` |
| `order_id=finish` 또는 `finish` | 결제 완료 화면 전환 (아래 주의) | `GATT_SUCCESS` + fff2에 `Order received` |
| 그 외 비어있지 않은 문자열 | `order_id=` 접두사 제거 후 주문 ID로 사용 → **GATT 서버 즉시 종료** | `GATT_SUCCESS` + fff2에 `Order received` |
| 빈 문자열 | 파싱 실패 | `GATT_FAILURE` + fff2에 `Data is empty` |
| fff1 이외 특성 | 거부 | `GATT_FAILURE` |

- 페이로드는 UTF-8. `OrderDataParser`는 **비어있지 않으면 무엇이든 통과**시킨다.
  `order_id=` 접두사 제거와 `finish` 판정은 파서가 아니라 `CardFragment.kt:222-234`에 있다.
- 응답 JSON 실제 형태 (`OrderDataParser.kt:53`) — 콜론 뒤 공백에 주의:
  `{"status": "success", "message": "..."}`
- 응답은 fff2에 적재될 뿐이며 Scanner가 **직접 Read** 해야 받는다.
  fff2는 NOTIFY property를 선언하지만 **구현이 없다** (`notifyCharacteristicChanged`,
  `addDescriptor`, `onDescriptorWriteRequest` 모두 부재). Notify를 기다리면 영원히 안 온다.

> ⚠️ **`finish`는 사실상 도달 불가**: 첫 write로 주문을 보내면 그 즉시 서버가 내려가므로(§4-3)
> 두 번째 write를 할 수 없다. 첫 write에 `finish`를 보내면 `handlePaymentFinish()`가 타지만
> 거기서도 서버를 내린다(`CardFragment.kt:329`). **한 세션에 write는 1회뿐**이며,
> "주문 전송 → 완료 전송" 2단계는 BLE로 성립하지 않는다.

## 4. GATT 서버 수명 (가장 중요)

`CardFragment.kt`. 서버가 내려가는 지점이 **3곳**이며, Windows는 GATT DB를 캐싱하므로
서버가 내려가도 UI에는 연결·채널이 남는다.

| # | 트리거 | `stopAdvertiseAndGatt()` 호출 위치 |
|---|---|---|
| 1 | 광고 개시 후 **60초** 경과 (`scanTimer`, 선언 L482) | L491 |
| 2 | `AT+CONNECT` 수신 후 **60초** 경과 (`connectedTimer`, 선언 L504) | L519 |
| 3 | **주문 1건 수신 즉시** (`showPaymentDetail` 호출 *전*) | L242 |
| 4 | `AT+DISCONNECT` 수신 후 1초 | L204–214 |
| 5 | 클라이언트 절단 시 `isConnected == true`이면 | L348–369 |

`scanTimer`는 `onGattServerReady` → `startWaitingEffects()` 시점, 즉 **광고 개시와 동시에**
시작한다 (사용자가 "결제 시작"을 누른 직후).

**따라서 한 번의 광고 세션에 주문은 1건만 전송 가능하다.** 연속 전송하려면 상대에서
"결제 시작"을 다시 눌러야 한다.

## 5. 이쪽(Scanner)이 지켜야 할 순서

```
1. 스캔 → mcandle 발견
2. Connect
3. fff1에 "AT+CONNECT" write        ← 필수. 안 보내면 60초 뒤 서버가 내려감
4. fff2 read → "Connected" 확인      ← Notify 안 옴. 반드시 직접 Read
5. fff1에 주문 ID write             ← 이 시점에 상대 서버가 종료됨
6. fff2 read → "Order received" 확인 ← 3~5의 성패는 이걸 읽어야만 알 수 있음
```

> 연결 직후(3번 이전)의 Read는 상대가 아직 응답을 적재하지 않아 기본값
> `{"status": "success", "message": "No data"}`를 돌려준다. 이걸 주문 정보로 오인하지 말 것.

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
