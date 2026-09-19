# Spec 003 — POS 비콘 시뮬레이터 (iBeacon 트리거 + GATT 수신)

- **상태**: 초안 — **합의 전. 구현 착수 금지.**
- **관련**: [protocol.md](protocol.md) (프로토콜 초안), [spec 001](../001-ble-scanner-mvp/spec.md)
- **주의**: 이 spec은 기존 제품과 **다른 시스템**이다. spec 001·002의 연장이 아니다.

## 목적 (Why)

UWB 멤버십 결제의 **POS 측**을 만든다. 손님이 폰을 꺼내거나 조작하지 않고, **주머니에 넣은 채로**
카운터에 서면 멤버 ID와 UWB short address가 POS에 전달되는 것이 목표다.

1차는 **Windows PC 시뮬레이터**, 최종은 **Android 11 POS 단말**에 올린다.
따라서 이 시뮬레이터는 **Android 11이 할 수 있는 범위 안에서만** 동작해야 한다 —
Windows 전용 기능을 쓰면 이식할 때 버린다.

## 기존 제품과의 관계

| | spec 001·002 (현행) | spec 003 (신규) |
|---|---|---|
| 이쪽 역할 | Central (스캔·연결) | **Peripheral(광고) + GATT 서버** |
| 상대 | mcandle Android 앱 | **손님 앱 (iOS·Android, 신규 개발)** |
| 데이터 방향 | POS → 폰 (주문번호) | **폰 → POS (멤버 ID·UWB addr)** |
| 트리거 | 사람이 "결제 시작" 탭 | **POS의 iBeacon이 폰을 깨움** |
| 최종 타겟 | Windows PC | **Android 11 POS** |

**공유하는 것은 거의 없다.** 재사용 가능한 것은 스캔 루프와 광고 파싱·중복 제거 정도다.

## 사용자 스토리

1. 손님은 앱을 설치하고 권한을 한 번 허용해두면, 이후 **폰을 꺼내지 않고** 카운터에 서는 것만으로
   멤버 확인이 된다.
2. 앱이 종료돼 있어도 POS 근처에 가면 **OS가 앱을 되살려** 동작한다.
3. 점원은 POS 화면에서 멤버 조회 결과를 본다.
4. 개발자는 Android POS 없이 **PC만으로** 손님 앱을 개발·검증할 수 있다.

## 기능 요구사항

### PC 시뮬레이터 (이 리포의 산출물)

- **FR-1 iBeacon 광고**: [protocol.md §2-1](protocol.md) 포맷으로 상시 송출. Proximity UUID /
  Major / Minor를 UI에서 변경 가능.
- **FR-2 Scan Response**: GATT 서비스 UUID 송출 (§2-2).
- **FR-3 GATT 서버**: `nonce`(READ) / `payload`(WRITE) / `result`(READ·NOTIFY) 3개 특성 제공 (§3).
- **FR-4 nonce 발급·검증**: READ마다 새 난수 발급, 유효시간 경과 또는 불일치 시 write 거부 (§4).
- **FR-5 payload 디코딩**: 16바이트를 멤버 ID(BCD)·UWB addr·nonce로 분해해 화면과 로그에 표시.
- **FR-6 서버 조회**: 멤버 ID로 조회 API 호출 후 결과를 `result`에 적재. **1차는 목(mock)으로 충분.**
- **FR-7 로그**: 광고 송출, 연결, 각 GATT 조작, nonce 검증 결과를 기존 Activity Log 형식으로 기록.
- **FR-8 Android 11 호환 범위 준수**: 레거시 광고 31바이트, 기기 이름 미포함, 확장 광고 미사용.

### 범위 밖

- **손님 앱 (iOS·Android)** — 별도 리포·별도 팀
- **Android 11 POS 이식** — 이 리포가 아니라 POS 앱 프로젝트
- 실제 멤버 조회 서버 연동 (1차 mock)
- 회전 토큰 기반 추적 방지 (2차)
- HMAC 서명 (2차, 자리만 예약)
- UWB 레인징 자체 — 이 프로토콜은 UWB **주소 교환**까지만 담당

## 비기능 요구사항

- constitution §1 준수: 전 과정 비동기, UI 프리징 없음.
- constitution §5 준수: 모든 BLE 호출 예외 처리, UI가 상태를 거짓으로 표시하지 않을 것.
- 광고와 스캔·GATT 서버가 **동시에** 동작할 것 (dual role).
- 프로토콜 변경 시 [protocol.md](protocol.md)를 먼저 고치고 구현이 따라갈 것.

## ⚠️ constitution 충돌 — 승인 필요

이 spec은 현행 원칙 두 개와 충돌한다. **구현 전에 결정이 필요하다.**

**충돌 1 — §2 단순성 (단일 파일 `main.py`)**

Peripheral(광고) + GATT 서버 + 기존 Central 기능을 한 파일에 담으면 `main.py`가 감당하기
어려워진다. §2는 *"모듈 분리는 spec으로 합의된 후에만"* 이라고 정해두었으므로, **이 spec이
그 합의 지점**이다.

> 제안: `ble/scanner.py`, `ble/advertiser.py`, `ble/gatt_server.py`, `ui/` 로 분리.
> **또는** spec 003을 별도 리포로 분리 (역할·상대·타겟이 모두 다르므로).

**충돌 2 — §3 ble-advertiser 인코딩 규약**

§3은 MINIMAL 광고 UUID의 카드번호·전화번호 배치를 불변 원칙으로 규정한다. spec 003은
**완전히 다른 프로토콜**(iBeacon + GATT)을 쓴다. §3이 003에 적용되지 않음을 명시해야 한다.

> 제안: §3의 적용 범위를 *"spec 001·002 계열(mcandle 광고 장치 연동)에 한한다"* 로 한정.

**그 외 영향**: DESIGN.md의 한 줄 설명과 시스템 경계가 "Scanner 전용"으로 되어 있어 갱신이
필요하다. PEER_CONTRACT.md는 spec 001·002의 상대(ble-advertiser)를 다루므로 그대로 두고,
003의 상대(손님 앱)는 protocol.md가 대신한다.

## 완료 기준 (Acceptance)

- [ ] PC가 iBeacon을 송출하고, 시판 비콘 스캐너 앱(iOS/Android)에서 UUID·Major·Minor가 보인다
- [ ] iOS 앱이 **종료 상태에서** region 진입으로 깨어난다 (PoC)
- [ ] Android 앱이 **프로세스 종료 상태에서** PendingIntent 스캔으로 깨어난다 (PoC)
- [ ] 폰이 PC의 GATT 서버에 연결해 nonce를 읽고 payload를 쓴다
- [ ] 잘못된/만료된 nonce로 쓰면 PC가 거부하고 로그에 남는다
- [ ] PC가 멤버 ID(10자리)와 UWB addr을 정확히 복원해 표시한다
- [ ] 광고와 GATT 서버가 동시에 동작한다 (연결 중에도 광고 지속)
- [ ] **깨어남 지연 실측치**가 기록된다 (화면 꺼짐·잠금 상태, 플랫폼별)

## 선행 조건 — PoC 먼저

**구현보다 검증이 앞선다.** 아래 두 개가 안 되면 설계 전체가 무너진다:

1. **깨어남 지연** — 주머니 속(화면 꺼짐·잠금) 상태에서 iOS region 진입과 Android
   PendingIntent 스캔이 **몇 초 만에** 깨어나는가? 카운터에서 15초를 기다릴 수는 없다.
2. **PC dual role** — Windows에서 광고 + GATT 서버 + 스캔이 동시에 되는가? 어댑터 의존적이다.

1번이 느리면 **2단계 비콘**(매장 입구 비콘으로 미리 깨워두고, 카운터 비콘으로 즉시 반응)이
필요하다. 이건 매장 설치 요구사항이 바뀌는 문제라 일찍 확인해야 한다.
