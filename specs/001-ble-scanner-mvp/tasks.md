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

## 후속 (2026-08-23 상대측 계약 정합 작업)

- [x] T12a. 연결 유실 감지: Bleak `disconnected_callback` 등록, UI 상태·Send 버튼 초기화 (`66c6a10`)
- [x] T12b. `AT+CONNECT` 핸드셰이크 전송 (ble-advertiser 대기 타이머 취소) (`66c6a10`)
- [x] T12c. 고정 Read 채널(fff2) 초기 Read 누락 버그 수정 (`66c6a10`), 명령 후 응답 Read (`175247e`)
- [x] T13. UUID 파싱 정정: 카드/전화 필드 뒤바뀜 수정, 송신측 실제 인코딩과 정합.
      데모 데이터용 휴리스틱(`010`/`1234` prefix)을 실제 배치 판정으로 대체 (`b63d9a7`, `9540b64`)

- [x] T16. 채널 선정 견고화: `fff0` 내 short UUID 매칭 + fallback에서 SIG base 배제 (`237f2e2`)
- [x] T17. 특성을 객체(handle)로 지정 — 중복 특성 대응 (`da02042`), 링크 사망 시 순회 중단 (`c1f079b`)
- [x] T18. MAC 회전 대응: 광고 내용 기준 장치 중복 제거 (`b49a594`)
- [x] T19. 레이아웃 반응형 전환: 좌측 두 패널 `expand` 기반 + 테이블 좌우 스크롤 (`cd9f482`)
- [x] T20. 상대측 계약 문서화 + `ble-peer-analyst` 에이전트 (`1360c45`, `ea099e3`, `8c48cb4`)

## 미완 (차기 spec 후보)

- [ ] T12d. 자동 재연결 (연결 유실 시 사용자 확인 후 재시도)
- [ ] T14. Notify 구독 지원 검토 (현재 Read 폴링/1회 읽기만 존재)
- [ ] T15. 상대측 1회 전송 제약 대응 — 전송 후 자동 재연결 또는 UI 안내 (PEER_CONTRACT §4)
