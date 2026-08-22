# Plan 002 — GATT 연결 안정화

- **상태**: 🚧 진행 중
- **spec**: [spec.md](spec.md)

## 1. 접근 방법 (How)

### 연결 상태 관리
- `BLEScannerApp`에 명시적 상태 필드 도입: `conn_state ∈ {IDLE, CONNECTING, CONNECTED, DISCONNECTED}`.
- 상태 전환은 단일 헬퍼(`set_conn_state`)로만 수행하여 UI(상태줄, Send 버튼,
  Connect/Disconnect 버튼)와 항상 동기화.

### 끊김 감지
- `BleakClient(address, disconnected_callback=self.on_remote_disconnect)` 사용.
- 콜백은 bleak 내부 스레드/루프에서 호출될 수 있으므로 UI 갱신은
  `page.run_task()` 경유로 안전하게 위임.

### 재시도
- `connect_device` 내부에 재시도 루프: 최대 2회 추가 시도, 1s → 2s 백오프.
- 각 시도를 `[CONNECT] attempt k/3` 형식으로 로깅 (constitution 제3조).

### UI
- DataTable의 Connect 버튼: 연결된 장치 행에서는 "Disconnect"로 라벨·핸들러 전환.
- 기존 좀비 연결 방지 로직(`disconnect_current_device`)은 그대로 재사용.

## 2. 영향 범위

- `main.py`만 수정 (단일 파일 유지). 신규 의존성 없음.
- `README.md` 연결 로직 설명, `DESIGN.md` §3.3·§6, `CHANGELOG.md` 갱신 필요.

## 3. 리스크

| 리스크 | 대응 |
|---|---|
| WinRT에서 disconnected_callback 지연·미호출 사례 | Send 실패 시에도 상태를 DISCONNECTED로 강등하는 이중 안전장치 |
| 재시도 중 사용자 조작(스캔 재시작 등) 충돌 | 재시도 루프가 `conn_state` 변화를 확인하고 중단 |

## 4. 검증

- 실기기 시나리오: 연결 후 iOS 앱 종료 → 끊김 감지 확인, 범위 이탈 → 재시도 로그 확인.
- 로그 파일로 상태 전환 시퀀스 검증.
