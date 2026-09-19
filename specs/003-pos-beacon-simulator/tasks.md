# Tasks 003 — POS 비콘 시뮬레이터

> **spec 승인 전. T0 결정이 나기 전에는 어떤 구현 태스크도 시작하지 않는다.**

## T0. 선행 결정 (사용자)

- [ ] T0a. **iOS 지원 확정** — 확정이면 데이터 회신은 GATT 고정 (광고 회신 불가)
- [ ] T0b. **constitution §2 충돌** — 모듈 분리할 것인가, spec 003을 **별도 리포**로 뺄 것인가
- [ ] T0c. **constitution §3 적용 범위** — "spec 001·002 계열에 한한다"로 한정할 것인가
- [ ] T0d. **Proximity UUID / GATT Service·Characteristic UUID** 값 확정 (protocol.md §7)
- [ ] T0e. **Major/Minor 할당 규칙** — 매장·단말 ID 체계

## Phase 0 — PoC (구현보다 먼저)

- [ ] T1. PC에서 iBeacon 송출 최소 스크립트 → 시판 비콘 스캐너 앱으로 수신 확인
- [ ] T2. **깨어남 지연 실측** — iOS region / Android PendingIntent, 화면 꺼짐·잠금 상태
      10회씩, 중앙값·최대값 기록
- [ ] T3. PC dual role 확인 — 광고 + GATT 서버 + 스캔 동시 실행
- [ ] T4. T1~T3 결과를 spec.md Acceptance와 protocol.md에 반영. **여기서 설계 재검토**

## Phase 1 — 골격

- [ ] T5. T0b 결정에 따라 모듈 분리 또는 리포 분기
- [ ] T6. iBeacon 광고 송출 (UUID/Major/Minor를 UI에서 변경 가능)
- [ ] T7. Scan Response에 GATT 서비스 UUID 송출
- [ ] T8. GATT 서버 — `nonce`/`payload`/`result` 3개 특성 등록

## Phase 2 — 프로토콜

- [ ] T9. nonce 발급·유효시간 검증
- [ ] T10. payload 디코더 (순수 함수, 실기기 없이 테스트 가능하게)
- [ ] T11. 멤버 조회 mock + `result` 적재

## Phase 3 — UI·문서

- [ ] T12. 광고 상태 패널 + 수신 이벤트 목록
- [ ] T13. 단계별 경과 시간 로깅 (spec 002 방식 재사용)
- [ ] T14. protocol.md를 루트 `PROTOCOL.md`로 승격 (확정 후)
- [ ] T15. DESIGN.md·CHANGELOG 갱신, constitution 개정 반영

완료 시 커밋 해시를 항목 끝에 병기한다: `- [x] T1. … (abc1234)`
