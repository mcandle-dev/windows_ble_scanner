# Plan 003 — POS 비콘 시뮬레이터

spec: [spec.md](spec.md) · 프로토콜: [protocol.md](protocol.md)

> **spec 승인 전이므로 이 계획도 확정이 아니다.** 특히 §constitution 충돌 결정(모듈 분리 /
> 별도 리포)에 따라 "구현 접근"이 통째로 바뀐다.

## 기술 선택

| 선택 | 근거 | 대안 / 위험 |
|---|---|---|
| Peripheral 구현: **WinRT 직접 호출** | `GattServiceProvider`·`BluetoothLEAdvertisementPublisher` 바인딩이 **이미 설치돼 있다** (bleak 의존성으로 들어온 `winrt-Windows.Devices.Bluetooth.Advertisement`, `...GenericAttributeProfile`). 새 의존성 0 | `bless` 라이브러리가 더 편하지만 의존성이 늘고, Windows 지원 범위가 버전마다 다름 |
| Central 유지: **Bleak** | 기존 코드 재사용 | — |
| UI: **Flet 유지** | 기존 자산·로그 패널 그대로 | — |
| iBeacon 바이트 조립: 수작업 | 포맷이 23바이트로 고정이라 라이브러리 불필요 | — |

**중요**: WinRT `BluetoothLEAdvertisementPublisher`로 manufacturer data(0x004C)를 실을 수
있는지, 그리고 `GattServiceProvider`와 **동시 실행**이 되는지를 PoC에서 먼저 확인한다.
Windows가 Apple Company ID 사용을 막지 않는지도 확인 대상이다.

## 구현 접근

### Phase 0 — PoC (구현 전 필수)

1. **PC iBeacon 송출** — 최소 스크립트로 WinRT 광고만 띄우고, 시판 비콘 스캐너 앱으로 수신 확인.
   → 안 되면 USB BLE 동글 또는 별도 비콘 하드웨어로 전략 변경.
2. **깨어남 지연 실측** — iOS(Always 권한) / Android(PendingIntent) 각각, 화면 꺼짐·잠금
   상태에서 진입 감지까지 걸리는 시간을 10회 측정해 중앙값·최대값 기록.
3. **dual role 확인** — 광고 + GATT 서버 + 스캔 동시 실행.

Phase 0 결과를 spec의 Acceptance와 protocol.md에 반영한 뒤 Phase 1로 넘어간다.

### Phase 1 — 골격

4. constitution 충돌 결정에 따라 **모듈 분리** 또는 **별도 리포 분기**.
5. `advertiser` — iBeacon 조립·송출, UUID/Major/Minor를 UI에서 변경.
6. `gatt_server` — 3개 특성(`nonce`/`payload`/`result`) 등록, READ/WRITE 핸들러.

### Phase 2 — 프로토콜

7. `nonce` 발급기 — 난수 생성, 발급 시각 기록, 유효시간 검증.
8. `payload` 디코더 — 16바이트 → 버전·멤버 ID(BCD)·UWB addr·nonce. **순수 함수로 분리**해
   실기기 없이 테스트 가능하게 한다 (spec 001의 `decode_uuid_data`가 그랬듯).
9. `result` 적재 + 멤버 조회 mock.

### Phase 3 — UI·로그

10. 광고 상태 패널(송출 중/UUID/Major/Minor), 수신 이벤트 목록(시각·멤버 ID·UWB addr·nonce 검증).
11. 기존 Activity Log·저장 기능 재사용.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| **깨어남 지연 15초+** | 설계 전체 무효 | Phase 0에서 먼저 측정. 느리면 2단계 비콘(입구+카운터)으로 설계 변경 |
| Windows가 Apple Company ID 광고를 막음 | 시뮬레이터 불가 | PoC로 확인. 막히면 동글 또는 전용 비콘 하드웨어 |
| PC dual role 미지원 | 광고·스캔 분리 필요 | 어댑터 교체 또는 동글 추가 |
| 사용자가 앱 force stop | 복구 불가 | 기술로 못 막음. 온보딩·안내로 처리 |
| OEM 배터리 관리자가 FGS 종료 | Android 무응답 | PendingIntent 스캔 병행 (protocol.md §5) |
| iOS Always 권한 거부 | iOS 전체 무효 | 온보딩 UX 설계. 거부 시 수동 모드 제공 여부 결정 필요 |
| Android 11 POS 이식 시 기능 차이 | 재작업 | FR-8 준수 — Android가 못 하는 건 시뮬레이터도 안 쓴다 |
| 평문 브로드캐스트로 멤버 ID 추적 | 개인정보 | 1차 nonce로 재전송만 차단, 회전 토큰은 2차 |

## 검증 방법

자동 테스트는 **순수 함수 계층에만** 가능하다 (constitution: 실기기 검증 의존).

**단위 검증 (실기기 없이)**
- `payload` 디코더: 정상 16바이트, 버전 불일치, BCD 오류, nonce 불일치, 길이 부족
- iBeacon 바이트 조립: 30바이트 예산 초과 여부, 필드 오프셋

**실기기 시나리오**
1. 시판 비콘 스캐너 앱으로 PC의 iBeacon UUID·Major·Minor 확인
2. iOS 앱 종료 → 비콘 접근 → 깨어남 → GATT write 성공까지 end-to-end
3. Android 프로세스 종료 → 동일
4. 만료된 nonce로 write → PC가 거부하고 로그에 기록
5. 연결 중에도 광고가 유지되는지 (다른 폰이 동시에 발견 가능한지)
6. 각 단계 소요 시간 기록 (spec 002에서 만든 경과 시간 로깅 방식 재사용)
