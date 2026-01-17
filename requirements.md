\# Project: Windows BLE Scanner \& Data Decoder



\## 1. Overview

\- Windows 환경에서 동작하는 BLE(Bluetooth Low Energy) 스캐너 개발.

\- 특정 장치(Advertiser)가 송출하는 Service UUID에서 데이터를 추출하여 UI에 표시하고, 장치와 연결하여 데이터를 주고받는 기능을 포함함.



\## 2. Technical Stack

\- \*\*Language:\*\* Python 3.10+

\- \*\*BLE Library:\*\* `bleak` (Windows 비동기 블루투스 제어)

\- \*\*UI Framework:\*\* `flet` (Flutter 기반 Python GUI)

\- \*\*Reference Logic:\*\* \[ble-advertiser](https://github.com/mcandle-dev/ble-advertiser)의 데이터 인코딩 방식 역추적



\## 3. Detailed Features



\### A. Scanning \& Data Decoding (Key Feature)

\- 주변 BLE 장치를 실시간으로 스캔함.

\- \*\*Decoding Logic:\*\* - 검색된 장치의 `service\_uuids` 리스트를 분석함.

&nbsp; - UUID 형식(128-bit)에 임베딩된 16진수 데이터를 텍스트(UTF-8/ASCII)로 변환.

&nbsp; - 변환된 데이터에서 \*\*'전화번호'\*\*와 \*\*'카드번호'\*\*를 파싱하여 추출함.

\- \*\*UI Display:\*\* 스캔 리스트에 \[장치 이름, 전화번호, 카드번호, RSSI(신호세기)]를 표 형태로 노출함.



\### B. Connection \& Reading

\- 리스트에서 특정 장치를 클릭하면 해당 MAC Address로 연결(`connect`) 시도.

\- 연결 완료 후, 장치의 GATT 서비스를 탐색하여 `order\_id` 정보를 가지고 있는 Characteristic을 찾음.

\- 해당 특성에서 데이터를 읽어와(Read) 화면의 'Order Information' 영역에 표시함.



\### C. Data Transmission (Write)

\- 사용자가 텍스트를 입력할 수 있는 필드와 'Send' 버튼 제공.

\- 연결된 장치의 특정 쓰기 가능 특성(Write Characteristic)에 데이터를 전송함.



\## 4. Development Constraints

\- 모든 BLE 작업은 `asyncio`를 통한 비동기 방식으로 처리하여 UI 프리징을 방지할 것.

\- Windows의 블루투스 권한 및 스택 특성을 고려하여 예외 처리를 철저히 할 것.

\- 가급적 단일 파일(`main.py`) 또는 명확한 모듈 구조로 작성할 것.

