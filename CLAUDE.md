# CLAUDE.md

Windows용 BLE 스캐너/디코더 (Flet + Bleak, 단일 파일 `main.py`).

## 문서 지도 — 코드를 읽기 전에

- **불변 원칙**: [constitution.md](constitution.md) — 모든 변경이 지켜야 할 규칙
- **현행 설계**: [DESIGN.md](DESIGN.md) — 시스템 경계, 구성 요소, 알려진 제약
- **상대측 계약**: [PEER_CONTRACT.md](PEER_CONTRACT.md) — 광고 인코딩·GATT 프로토콜·서버 수명
- **작업 단위**: [specs/](specs/) — 기능별 spec/plan/tasks. 새 기능은 코드 전에 spec부터
- **이력**: [CHANGELOG.md](CHANGELOG.md), `logs/work_log_*.md`

## 실행

```bash
pip install -r requirements.txt
python main.py
```

## 환경 제약 (중요)

- **Windows + Bluetooth 하드웨어에서만 동작·검증 가능** (Bleak WinRT 백엔드).
  Linux/원격 환경에서는 실행 불가 — 코드 변경 시 정적 검토(`python -m py_compile main.py`)까지만
  가능하고, 실기기 검증은 사용자 몫임을 명시할 것.
- 자동 테스트 없음. 검증 시나리오는 mcandle iOS 앱(리포의 zip 참조)과의 수동 연동.

## 상대측 의존 (이 리포 코드만 봐서는 절대 못 푸는 것)

이 앱은 Central(Scanner)일 뿐이고, 실제 동작은 광고 장치 쪽 구현에 달려 있다.
**현행 상대는 Android 앱 `mcandle-dev/ble-advertiser`** (로컬: `D:\dev\mcandle\ble-advertiser`).
동봉된 `mcandle-ios-app.zip`은 과거 참조물이며 현재 검증 대상이 아니다.

- 연결·전송·디코딩이 안 되면 **먼저 `ble-peer-analyst` 에이전트를 돌려라.**
  상대가 예고 없이 바뀌어 계약이 깨진 경우가 실제로 반복됐다.
- 상대는 **주문 1건을 받으면 GATT 서버를 즉시 내린다.** "연결은 됐는데 Send가 안 된다"의
  대부분이 이것 아니면 60초 타임아웃이다. 자세한 건 PEER_CONTRACT.md §4.
- BLE 동작(UUID 상수, 명령어, 디코딩 규칙)을 바꾸기 전에도 이 에이전트로 현재 계약을 확인할 것.

## 함정 (코드만으로 파악하기 어려운 것)

- Flet 0.80.x는 breaking change가 잦다: 색상/아이콘은 문자열 리터럴 유지, `FilePicker` 사용 금지
  (과거 UI 깨짐으로 제거됨), 코루틴 핸들러는 `page.run_task()` 경유.
- Write는 **With Response가 기본** — Without Response는 iOS 측에서 유실된 전력이 있음.
- GATT 시스템 특성(2a00 등)에 접근하면 Windows에서 Access Denied — 블랙리스트를 유지할 것.

## 작업 규칙

1. 새 기능은 `specs/NNN-이름/`에 spec.md → plan.md → tasks.md 작성 후 구현 (`/sdd-new-spec` 스킬).
2. 동작 변경 시 `CHANGELOG.md` 갱신, 설계 변경 시 `DESIGN.md` 갱신 (`/wrap-up` 스킬).
3. 커밋 메시지는 기존 관례(영문, `feat:`/`fix:` 혼용) 유지.
