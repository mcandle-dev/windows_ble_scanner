# Tasks 002 — Connect & Send

- [x] T1. `send_data`에서 전송 로직을 `send_order()`로 분리, 버튼 핸들러는 이를 호출만
- [x] T2. `send_handshake()`가 성공 여부를 bool로 반환하도록 변경
- [x] T3. `auto_send_switch` 추가 (기본 ON), Connection Information 헤더에 배치
- [x] T4. `connect_device` 말미에 자동 전송 연결 — 핸드셰이크 성공 + 메시지 있음 + 스위치 ON
- [x] T5. 단계별·전체 소요 시간 로그, 60초 초과 시 경고
- [x] T6. 스캔 주기 단축 (`discover` 5s→3s, sleep 1s→0.5s)
- [x] T7. 문서 갱신 — CHANGELOG, DESIGN.md(흐름·구성요소)

완료 시 커밋 해시를 항목 끝에 병기한다: `- [x] T1. … (abc1234)`
