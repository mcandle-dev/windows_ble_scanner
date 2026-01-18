# 기술 스택 문서 (Technical Stack Documentation)

이 문서는 프로젝트에 사용된 핵심 기술인 **Flet**과 **Bleak**에 대한 개요를 제공합니다.

## 1. Flet (GUI 프레임워크)
**Flet**은 프론트엔드 경험 없이도 Python만으로 대화형 웹, 데스크톱, 모바일 앱을 구축할 수 있게 해주는 프레임워크입니다. 이 애플리케이션의 사용자 인터페이스(UI)를 구성하는 데 사용되었습니다.

### 주요 사용 개념
- **페이지 및 컨트롤(Page & Controls)**: 전체 UI는 `page` 캔버스 위에 `Row`(행), `Column`(열), `Container`, `DataTable`, `ListView`와 같은 컨트롤(위젯)들을 추가하여 구성됩니다.
- **비동기 UI 업데이트(Asynchronous UI Updates)**: 실시간 스캔 결과와 로그를 동적으로 표시하기 위해 `page.update()`를 사용하여 UI 상태를 즉시 갱신합니다.
- **이벤트 처리(Event Handling)**: 사용자 상호작용(버튼 클릭, 입력 필드 변경 등)은 Python 메서드와 연결된 이벤트 핸들러 함수(예: `on_click`, `on_change`)를 통해 처리됩니다.
- **반응형 레이아웃(Responsive Layout)**: 애플리케이션 창 크기 조절에 유연하게 대응하기 위해 `Row`와 `Column` 컨트롤 내에서 `expand=True` 및 `flex` 속성을 활용합니다.

### 왜 Flet인가?
- **Python 중심**: HTML/CSS/JS 지식이 전혀 필요 없습니다.
- **크로스 플랫폼**: 단일 코드베이스로 Windows, macOS, Linux, Web에서 모두 실행됩니다.
- **성능**: Flutter를 기반으로 구축되어 부드러운 60fps 성능을 제공합니다.

## 2. Bleak (저전력 블루투스)
**Bleak**은 Bluetooth Low Energy platform Agnostic Klient의 약자로, Python에서 비동기 BLE 통신을 위한 표준 라이브러리입니다.

### 구현된 핵심 컴포넌트
- **BleakScanner**:
  - 주변의 BLE 장치를 검색하는 데 사용됩니다.
  - `discover(return_adv=True)`를 사용하여 연결하지 않고도 Advertisement Data(UUID, 제조사 데이터, RSSI)에 즉시 액세스합니다.
- **BleakClient**:
  - 특정 BLE 장치와의 연결을 관리합니다.
  - GATT(Generic Attribute Profile) 클라이언트 작업을 처리합니다.
- **GATT 작업**:
  - **서비스 탐색**: `client.services`를 순회하여 장치가 제공하는 기능을 매핑합니다.
  - **읽기(Read)**: `read_gatt_char(uuid)`를 사용하여 특성(Characteristics)에서 데이터를 가져옵니다.
  - **쓰기(Write)**: `write_gatt_char(uuid, data)`를 사용하며, `response` 플래그를 통해 "응답 있음"과 "응답 없음" 방식을 모두 지원합니다.

### 비동기 설계 (Asynchronous Design)
- Bleak은 Python의 `asyncio`를 기반으로 구축되었습니다. 이를 통해 스캐너가 백그라운드에서(non-blocking) 실행되는 동안에도 UI가 멈추지 않고 사용자의 동작에 반응할 수 있습니다.
