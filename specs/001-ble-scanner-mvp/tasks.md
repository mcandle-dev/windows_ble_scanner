# Tasks 001 — BLE Scanner MVP

- **상태**: ✅ 전체 완료 (소급 기록 — git 히스토리·CHANGELOG 기준)

## Phase 1 — 스캔·디코딩 (2026-01-18, cf0e12b)
- [x] T1. Flet 기본 레이아웃 + Dark 테마 + Start/Stop Scan 토글
- [x] T2. `BleakScanner.discover(return_adv=True)` 스캔 루프
- [x] T3. UUID 디코딩: Literal Hex 세그먼트 파싱 (전화/카드)
- [x] T4. UUID 디코딩: ASCII 변환 정규식 fallback
- [x] T5. 장치 이름 필터 (대소문자 무시 like 검색)
- [x] T6. `page.run_task()`로 코루틴 실행 경고 해결

## Phase 2 — GATT 통신 (7fe3be3 ~ 91641f2)
- [x] T7. 장치 연결 및 전체 Service/Characteristic 탐색·로깅 (e020fc2)
- [x] T8. Read 특성 자동 선정 및 Order Information 표시
- [x] T9. Write 특성 자동 선정, Response 방식 자동 결정 (ed6c8c2)
- [x] T10. 시스템 GATT 특성 제외로 Access Denied 회피 (91641f2)
- [x] T11. Connect/Send 상세 디버그 로깅 (162db2e)

## Phase 3 — UI·로그·안정화 (2026-01-19 ~ 01-25)
- [x] T12. 50:50 분할 레이아웃 + 드래그 리사이즈 (8839f39)
- [x] T13. 로그 자동 저장 (`logs/ble_*.txt`, FilePicker 제거) (8839f39)
- [x] T14. 고정 채널 UUID(`fff1`/`fff2`) 우선 정합 로직
- [x] T15. iOS 수신 신뢰성: Write With Response 기본값 + UI 스위치 (a0b91bd)
- [x] T16. 좀비 연결 방지: 명시적 disconnect (db04a7b)
- [x] T17. `requirements.txt` 버전 고정 (0f6657a)
