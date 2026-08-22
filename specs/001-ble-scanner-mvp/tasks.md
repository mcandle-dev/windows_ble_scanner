# Tasks 001 — BLE Scanner MVP (소급 기록)

완료 항목은 해당 커밋으로 추적한다.

## 완료

- [x] T1. 프로젝트 초기화: Flet UI 골격 + Bleak 스캔 루프 + UUID 디코딩 (`cf0e12b`)
- [x] T2. 장치 이름 필터(like-search) 및 스캔 버튼 상태 표시 (`cf0e12b`)
- [x] T3. GATT 연결·서비스 탐색·상세 로깅, `BleakClient.services` 오류 수정 (`e020fc2`, `13f12e7`)
- [x] T4. Write 채널 선정 로직 + 오류 처리 개선 (`ed6c8c2`)
- [x] T5. 시스템 GATT 특성 제외로 Access Denied 회피 (`91641f2`)
- [x] T6. Connect/Send 디버그 로깅 강화 (`162db2e`)
- [x] T7. UI 50:50 분할 + 드래그 리사이즈 + 로그 자동 저장(`logs/`) (`8839f39`)
- [x] T8. requirements.txt 고정 (`0f6657a`)
- [x] T9. Write With Response 기본값 전환 (iOS 수신 신뢰성) (`a0b91bd`)
- [x] T10. 재연결 로직 수정(명시적 disconnect) + Connection Information 레이아웃 개선 (`db04a7b`)
- [x] T11. 문서화: README 로직 설명(한국어), TECHNICAL_STACK, CHANGELOG (`7fe3be3`, `cc779d3` 외)

## 미완 (차기 spec 후보)

- [x] T12a. 연결 유실 감지: Bleak `disconnected_callback` 등록, UI 상태·Send 버튼 초기화
- [x] T12b. `AT+CONNECT` 핸드셰이크 전송 (ble-advertiser 대기 타이머 취소)
- [x] T12c. 고정 Read 채널(fff2) 초기 Read 누락 버그 수정
- [ ] T12d. 자동 재연결 (연결 유실 시 사용자 확인 후 재시도)
- [ ] T13. UUID 파싱 정밀화: 제조사 데이터(manufacturer data) 패턴 지원, literal 판정
      휴리스틱(`010`/`1234` prefix) 정식화
- [ ] T14. Notify 구독 지원 검토 (현재 Read 폴링/1회 읽기만 존재)
