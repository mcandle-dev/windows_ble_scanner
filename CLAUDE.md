# CLAUDE.md

Windows BLE 스캐너 & 디코더 — Service UUID에 임베딩된 전화번호·카드번호를 디코딩하고
GATT Read/Write 통신하는 Flet 데스크톱 앱. 이 리포는 **SDD(Spec-Driven Development)**로 운영된다.

## 문서 지도 (여기서 찾을 것)

| 알고 싶은 것 | 문서 |
|---|---|
| 불변 원칙 (비동기, 예외 처리, 인코딩 스펙 등) | [constitution.md](constitution.md) |
| 현행 시스템 설계·데이터 흐름·알려진 한계 | [DESIGN.md](DESIGN.md) |
| 진행 중/완료된 작업의 spec·plan·tasks | [specs/](specs/) |
| 원 요구 정의 | [requirements.md](requirements.md) |
| 변경 이력 | [CHANGELOG.md](CHANGELOG.md) |

## 작업 규칙 (SDD)

1. 새 기능·구조 변경은 구현 전에 `specs/NNN-<slug>/`에 spec.md → plan.md → tasks.md를 작성한다
   (`/sdd-feature` 스킬 사용).
2. 구현이 끝나면 tasks 체크, `DESIGN.md`·`CHANGELOG.md` 갱신, 작업 로그를 남긴다
   (`/worklog` 스킬 사용).
3. constitution과 충돌하는 요청은 구현 전에 사용자에게 확인한다.

## 실행 환경 주의

- **런타임은 Windows 전용** (WinRT 기반 bleak). Linux/CI/원격 세션에서는 BLE 동작을
  실행·검증할 수 없다 — 문법 검사(`python -m py_compile main.py`)까지만 가능.
- 실기기 검증은 ble-advertiser 방식 Peripheral(iOS 앱)과의 페어 테스트로 사용자가 수행한다.
  검증이 필요한 변경은 검증 시나리오를 tasks에 명시할 것.

## 명령어

```bash
python -m venv venv && .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py
```
