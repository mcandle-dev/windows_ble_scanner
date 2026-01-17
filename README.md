# Windows BLE 스캐너 & 디코더

이 프로젝트는 Python의 **Bleak** 라이브러리와 **Flet** GUI 프레임워크를 사용하여 개발된 Windows용 BLE(Bluetooth Low Energy) 스캐너입니다. 주변 BLE 장치를 스캔하고, 특정 Service UUID에 숨겨진 데이터를 추출하여 화면에 표시합니다.

## 주요 기능

- **실시간 BLE 스캔:** 주변의 모든 BLE 장치를 실시간으로 검색하고 RSSI(신호 세기)를 모니터링합니다.
- **데이터 디코딩 서비스 (핵심 기능):**
  - 장치의 Service UUID에서 전화번호와 카드번호를 자동으로 추출하여 리스트에 노출합니다.
  - 대소문자 구분 없는 장치 이름 필터링(Like Search) 기능을 지원합니다.
- **GATT 서비스 상호작용:**
  - 장치 연결 후 서비스 및 특성(Characteristic) 탐색.
  - 특정 특성에서 데이터 읽기(Read) 및 쓰기(Write) 기능 제공.
- **현대적인 UI:** Dark 모드가 적용된 반응형 GUI (Flet 기반).

## 데이터 추출 로직 설명

이 프로그램은 [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser) 방식에 따라 Service UUID(128-bit) 내부에 임베딩된 데이터를 두 가지 방식으로 파싱합니다.

### 1. 직접 16진수 세그먼트 파싱 (Literal Hex Parsing)
UUID의 표준 형식(`8-4-4-4-12`)을 활용하여 데이터를 직접 읽어옵니다.
- **전화번호 (Phone Number):** UUID의 앞쪽 세 개 세그먼트(8+4+4 = 총 16자리)를 결합하여 표시합니다. 
  - 예: `12345678-1234-5670-xxxx-...` -> `1234567812345670`
- **카드번호 (Card Number):** UUID의 네 번째 세그먼트(4자리)를 추출합니다.
  - 예: `xxxx-xxxx-xxxx-2222-xxxx` -> `2222`

### 2. ASCII 문자열 변환 파싱 (ASCII Fallback)
UUID 전체의 16진수 값을 ASCII 텍스트로 변환한 뒤 정규표현식을 통해 데이터를 찾습니다.
- **전화번호:** `010`으로 시작하는 11자리 숫자를 검색합니다.
- **카드번호:** 8~16자리의 연속된 숫자를 검색합니다.

## 환경 설정 및 설치

### 요구 사항
- Python 3.10 이상
- Windows OS (Bluetooth 하드웨어 필요)

### 설치 방법
1. 저장소 복제:
   ```bash
   git clone https://github.com/mcandle-dev/windows_ble_scanner.git
   cd windows_ble_scanner
   ```
2. 가상환경 생성 및 활성화:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. 필수 라이브러리 설치:
   ```bash
   pip install bleak flet
   ```

## 실행 방법
```bash
python main.py
```

## 프로젝트 구조
- `main.py`: 애플리케이션의 메인 로직 및 UI 코드.
- `logs/`: 일자별 작업 로그 파일 저장.
- `requirements.md`: 프로젝트 상세 요구 정의서.

## 저작권 및 참고
- 본 프로젝트는 사용자 요구사항에 따른 MVP(Minimum Viable Product) 버전입니다.
- 데이터 인코딩 방식 참고: [ble-advertiser](https://github.com/mcandle-dev/ble-advertiser)
