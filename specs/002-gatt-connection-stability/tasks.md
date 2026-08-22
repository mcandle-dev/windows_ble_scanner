# Tasks 002 — GATT 연결 안정화

- **상태**: 🚧 진행 중

## 완료 (기구현분 소급 기록)
- [x] T1. 스캔 중지·신규 연결 시 명시적 disconnect로 좀비 연결 방지 (db04a7b)
- [x] T2. 연결 성립 시 스캔 버튼 상태 자동 리셋 (db04a7b)

## 남은 작업
- [ ] T3. `conn_state` 상태 필드 및 `set_conn_state` 헬퍼 도입 (FR-1)
- [ ] T4. `disconnected_callback`으로 원격 끊김 감지, Send 비활성화 (FR-2)
- [ ] T5. 연결 재시도 루프 (최대 3회, 1s→2s 백오프, 시도별 로깅) (FR-3)
- [ ] T6. 연결된 장치 행의 버튼을 Connect ↔ Disconnect 토글로 전환 (FR-4)
- [ ] T7. Access Denied 시 Windows 페어링 절차 안내 메시지 구체화 (FR-5)
- [ ] T8. 문서 갱신: README 연결 로직 절, DESIGN.md §3.3·§6, CHANGELOG
- [ ] T9. 실기기 검증: 원격 끊김·범위 이탈·재시도 시나리오 로그 확보
