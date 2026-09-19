# mcandle UWB 멤버십 프로토콜 (초안 v0.1)

> **상태: 초안 — 합의 전.** 확정되면 리포 루트 `PROTOCOL.md`로 승격하고, PC 시뮬레이터 /
> Android POS / 손님 앱(iOS·Android) 네 구현체가 모두 이 문서를 기준으로 삼는다.

## 0. 참여자와 역할

| 참여자 | BLE 역할 | 비고 |
|---|---|---|
| **POS** | Peripheral (iBeacon 광고) + **GATT 서버** | 1차: Windows PC 시뮬레이터 / 최종: **Android 11 POS** |
| **손님 앱** | Central (스캔 + 연결 + write) | iOS, Android |
| 서버 | — | POS가 멤버 조회 |

**데이터 방향**: 손님 앱 → POS (멤버 ID, UWB short address)
POS는 받은 멤버 ID로 서버에 조회한다.

## 1. 전체 흐름

```
① POS: iBeacon 광고 상시 송출 (AdvData) + GATT 서비스 UUID (ScanResponse)
        │
        ├─ iOS     : Core Location region 진입 → 앱 기동 (종료 상태여도 OS가 되살림)
        └─ Android : PendingIntent 스캔 또는 FGS 스캔 → 앱 기동
        │
② 손님 앱: POS에 GATT 연결 (Central)
③ 손님 앱: nonce characteristic READ          ← 재전송 방지용 1회용 난수
④ 손님 앱: payload characteristic WRITE       ← 멤버 ID + UWB addr + nonce
⑤ POS   : write response = 접수 확인 (ACK)
⑥ POS   : 서버에 멤버 조회 → 결과를 result characteristic에 적재
⑦ 손님 앱: result READ (선택)
```

**왜 광고 회신이 아니라 GATT인가**: iOS 앱은 백그라운드에서 광고하면 Service UUID가
overflow 영역으로 들어가 **Apple 기기 외에는 읽을 수 없다**. iBeacon 형식으로 광고하는 것도
서드파티 앱에는 막혀 있다. 따라서 폰 → POS 방향은 **GATT 연결이 유일한 수단**이다.
Android도 같은 경로를 쓰면 양 플랫폼이 한 구현으로 합쳐진다.

## 2. POS 광고

### 2-1. Advertising Data — iBeacon (31바이트 예산 중 30B)

```
Flags                               3B
Manufacturer Data                  27B
  ├ AD length / type (0xFF)         2B
  ├ Company ID  0x004C (Apple)      2B
  └ iBeacon payload                23B
      ├ Type    0x02                1B
      ├ Length  0x15                1B
      ├ Proximity UUID             16B   ← 전사 공통 고정값
      ├ Major                       2B   ← 매장 ID
      ├ Minor                       2B   ← 단말 ID 또는 세션 카운터
      └ TxPower                     1B
                                  ────
                                   30B / 31B
```

- **기기 이름을 넣지 말 것** (`setIncludeDeviceName(false)`). 넣으면
  `ADVERTISE_FAILED_DATA_TOO_LARGE`.
- **Proximity UUID는 고정**이어야 한다. iOS가 이 값으로 region을 등록하므로 바꾸면 못 깨운다.
  매장 구분은 **Major**로 한다 (iOS 앱의 region 등록 한도가 20개다).

### 2-2. Scan Response (별도 31바이트)

```
128-bit GATT Service UUID          18B   ← 앱이 연결 대상을 찾는 데 사용
```

AdvData가 iBeacon으로 꽉 차므로 GATT 서비스 UUID는 여기에 싣는다.
Android: `startAdvertising(settings, advertiseData, scanResponse, callback)`.

## 3. GATT 서비스 (POS가 호스팅)

| 특성 | 속성 | 내용 |
|---|---|---|
| `nonce` | READ | 4B 난수. **READ 될 때마다 새로 생성**하고 유효시간을 건다 |
| `payload` | WRITE (with response) | 아래 3-1 |
| `result` | READ, NOTIFY | 조회 결과 JSON |

Service/Characteristic UUID는 **미정** — 확정 필요 (§7).

### 3-1. payload 포맷 (write, 16바이트)

```
[0]      version           1B   0x01
[1..5]   멤버 ID (BCD)     5B   10자리 → BCD 압축
[6..7]   UWB short addr    2B   예: 0x43 0x33
[8..11]  nonce 에코        4B   ③에서 읽은 값 그대로
[12..15] 예약              4B   0x00 패딩 (2차 HMAC 자리)
```

GATT write는 광고와 달리 **31바이트 제약이 없다**. 필드가 늘어나면 여유 있게 확장 가능하다.

### 3-2. result 포맷

```json
{"status": "success", "member": "...", "message": "..."}
```

## 4. 재전송(Replay) 방지

POS가 `nonce`를 매 READ마다 새로 발급하고, `payload`에 실려 돌아온 값이 **방금 발급한 것과
일치할 때만** 수락한다. 유효시간(예: 30초)을 넘기면 폐기한다.

이것으로 **녹음 후 재생 공격**이 막힌다. 다만 **추적(같은 멤버 ID가 반복 노출)** 은 막지
못한다 — 회전 토큰이 필요하며 2차 과제로 둔다.

2차 강화안: nonce를 그대로 돌려주는 대신
`HMAC-SHA256(공유키, nonce ‖ 멤버ID)`의 앞 4바이트를 `[12..15]`에 넣는다. 크기 변화 없음.

## 5. 플랫폼별 깨우기

| | 등록 API | 프로세스 죽어도 | 재부팅 후 |
|---|---|---|---|
| **iOS** | `startMonitoring(CLBeaconRegion)` | ✅ OS가 앱을 되살림 | ✅ |
| **Android ①** | `startScan(..., ScanCallback)` + FGS | ❌ | ❌ |
| **Android ②** | `startScan(..., PendingIntent)` | ✅ OS가 앱을 되살림 | ❌ |
| **Android ③** | `BOOT_COMPLETED` 리시버 | — | ✅ ①②를 재등록 |

**Android는 ①+②+③을 모두 써야 한다.** ①만 쓰면 OEM 배터리 관리자가 FGS를 죽였을 때 조용히
먹통이 되고, ②만 쓰면 매번 앱을 되살려야 해서 느리다.

**사용자가 앱을 강제 종료(force stop)하면 어떤 방법으로도 복구되지 않는다.** 제품 정책으로
다뤄야 할 문제다.

### Android ScanFilter는 필수

Android 8.1+는 **화면이 꺼진 상태에서 필터 없는 스캔 결과를 주지 않는다.** 주머니 속이
곧 화면 꺼짐이므로 정통으로 걸린다.

```kotlin
val prefix = byteArrayOf(0x02, 0x15) + proximityUuidBytes
ScanFilter.Builder()
    .setManufacturerData(0x004C, prefix, ByteArray(prefix.size) { 0xFF.toByte() })
```

`isOffloadedFilteringSupported()`가 true면 이 필터가 **블루투스 칩에서 처리**되어 CPU를
깨우지 않는다. 상시 스캔의 배터리 실현 가능성이 여기 달려 있다.

## 6. 권한

| 플랫폼 | 필요 권한 |
|---|---|
| iOS | 위치 **Always** (`requestAlwaysAuthorization`). When In Use로는 백그라운드 깨우기 불가 |
| Android ≤ 11 | `ACCESS_FINE_LOCATION` + **위치 서비스 ON** |
| Android 12+ | `BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT` |
| Android 10+ 백그라운드 | `ACCESS_BACKGROUND_LOCATION` (별도 설정 화면, 기본 거부) |

iOS의 Always와 Android의 백그라운드 위치는 **둘 다 사용자가 별도 화면에서 명시적으로 켜야
한다.** 온보딩 설계가 성패를 가른다.

## 7. 미정 — 확정 필요

1. **Proximity UUID** 값 (전사 공통 1개)
2. **GATT Service / Characteristic UUID** 3종
3. **Major/Minor 할당 규칙** — 매장 ID 체계
4. nonce 유효시간, 재시도 횟수·간격
5. `result` 응답 스키마 확정
6. 2차 HMAC 공유키 배포 방식
