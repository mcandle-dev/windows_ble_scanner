# Spec 001 — BLE Scanner MVP (소급 기록)

- **상태**: 구현 완료 (2026-01-25 기준, 커밋 `db04a7b`까지) / 일부 후속 과제 미완
- **작성 방식**: 이미 구현된 MVP를 SDD 전환 시점에 소급(retroactive) 기록함.
  원 요구사항 출처: `requirements.md`, `logs/work_log_2026-01-18.md`, `CHANGELOG.md`

## 목적 (Why)

iOS 광고 장치(mcandle)가 Service UUID에 임베딩해 송출하는 결제 관련 데이터(전화번호·카드번호)를
Windows PC에서 즉시 확인하고, 해당 장치와 GATT로 주문 정보를 주고받을 수 있는 검증 도구가 필요하다.

## 사용자 스토리

1. 운영자는 앱을 실행하고 Start Scan을 누르면, 주변 광고 장치의 이름·전화번호·카드번호·RSSI를
   표로 실시간 확인할 수 있다.
2. 운영자는 장치 이름으로 목록을 필터링(대소문자 무시, 부분 일치)할 수 있다.
3. 운영자는 목록에서 Connect를 눌러 장치와 연결하고, 장치가 가진 주문 정보(Order Information)를
   자동으로 읽어 확인할 수 있다.
4. 운영자는 텍스트 메시지를 입력해 연결된 장치로 전송할 수 있다.
5. 운영자는 세션 중 발생한 모든 이벤트 로그를 파일로 저장할 수 있다.

## 기능 요구사항

- **FR-1 스캔**: 주변 BLE 장치 실시간 검색, RSSI 표시. 필터(like-search) 지원.
- **FR-2 디코딩**: Service UUID에서 전화번호·카드번호 추출 (constitution §3 규칙).
- **FR-3 연결/탐색**: 연결 후 GATT 서비스·특성 전수 탐색 및 상세 로깅. 고정 UUID(fff1/fff2)
  우선, 속성 기반 fallback. 시스템 특성 제외.
- **FR-4 읽기**: Read 채널에서 데이터를 읽어 UTF-8 디코딩 후 Order Information에 표시.
- **FR-5 쓰기**: Write 채널로 UTF-8 전송. Response 여부 사용자 제어(스위치, 기본 With Response —
  iOS 수신 신뢰성 때문). Access Denied 시 페어링 필요 안내.
- **FR-6 로그**: 타임스탬프 로그를 UI 표시 + `logs/ble_*.txt` 저장.
- **FR-7 UI**: Dark 모드, 50:50 분할(드래그 리사이즈), 스캔 버튼 상태 표시(파랑/빨강),
  연결 시 스캔 자동 중지.

## 비기능 요구사항

- UI 프리징 금지 (전 BLE 작업 비동기).
- 좀비 연결 금지 (스캔 중지·재연결 시 명시적 disconnect).
- Flet 0.80.x 호환.

## 완료 기준 (Acceptance)

- [x] mcandle iOS 앱 광고를 스캔해 전화번호/카드번호가 표에 표시된다.
- [x] Connect 후 Order Information이 자동 표시된다.
- [x] Send로 iOS 앱에 메시지가 수신된다 (Write With Response 기본).
- [x] 로그 저장 버튼으로 `logs/` 파일이 생성된다.
- [ ] 연결 유실 시 자동 감지·복구 (후속 과제 → 차기 spec 후보)
- [ ] 제조사 데이터 패턴 기반 파싱 정밀화 (후속 과제 → 차기 spec 후보)
