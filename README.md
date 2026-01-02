# 🔔 Discord Alarm (Windows to Telegram)

Windows 알림 센터(Toast Notification)에 뜨는 Discord 알림을 감지하여, Telegram으로 실시간 전달하는 프로그램입니다.
시스템 트레이(System Tray) 모드를 지원하며, Python의 `asyncio`와 `winsdk`를 사용하여 CPU 리소스를 최소화(0~0.1%)했습니다.

## ✨ 주요 기능
- **저전력 모니터링:** 화면 캡처가 아닌 Windows OS 이벤트 리스너 방식 사용.
- **백그라운드 실행:** 닫기(X) 버튼 클릭 시 시스템 트레이 아이콘으로 숨겨짐.
- **텔레그램 연동:** Discord 알림 제목과 내용을 텔레그램 봇으로 즉시 전송.
- **GUI 로그:** 현재 작동 상태와 감지된 알림 내역을 실시간으로 확인 가능.

## 🛠️ 사전 준비 (Prerequisites)
- **OS:** Windows 10 또는 Windows 11
- **Python:** 3.10 이상
- **필수 파일:** 실행 파일과 같은 폴더에 `Bells.ico` 파일이 반드시 있어야 합니다.

## 📦 설치 방법 (Installation)

1. **가상환경 생성 및 활성화 (Conda)**
   ```bash
   conda create -n discord_alarm python=3.10
   conda activate discord_alarm

   ```

2. **패키지 설치**
`requirements.txt` 파일이 있다면 아래 명령어로 설치합니다.

   ```bash
   pip install -r requirements.txt

   ```


*(없다면 수동 설치: `pip install winsdk requests pystray Pillow pyinstaller`)*

## ⚙️ 설정 (Configuration)

`discord_alarm.py` 파일을 열어 상단의 변수 값을 본인의 정보로 수정하세요.

```python
TELEGRAM_TOKEN = "여기에_텔레그램_봇_토큰"
CHAT_ID = "여기에_CHAT_ID"
TARGET_APP_KEYWORD = "Discord"  # 감지할 앱 이름 (대소문자 구분 없음)
ICON_FILE_NAME = "Bells.ico"     # 아이콘 파일명

```

## ▶️ 실행 및 빌드 (Usage & Build)

### 1. 파이썬 직접 실행

```bash
python discord_alarm.py

```

### 2. EXE 실행 파일 만들기

`pyinstaller`를 사용하여 단일 실행 파일(.exe)로 변환합니다.

```bash
pyinstaller -w -F -i "Bells.ico" --name "DiscordAlarm" discord_alarm.py

```

> **옵션 설명:**
> * `-w`: 콘솔(검은 창) 숨기기
> * `-F`: 단일 파일로 생성
> * `--add-data`: 트레이 기능을 위해 아이콘 파일을 내부에 포함
> * `--hidden-import`: 필요한 라이브러리 강제 포함
> 
> 

빌드가 완료되면 `dist` 폴더 안에 **`DiscordAlarm.exe`** 파일이 생성됩니다.

## ⚠️ 주의 사항 & 문제 해결

* **Discord 설정:** 앱 설정 > 알림 > **'데스크톱 알림 활성화'**가 켜져 있어야 합니다.
* **방해 금지 모드:** Discord 상태가 '방해 금지(빨간색)'이거나, Windows가 '집중 지원 모드'일 경우 알림이 뜨지 않아 감지할 수 없습니다.
* **창 활성화 이슈:** PC에서 Discord 창을 보고 있는 상태(활성화)에서는 윈도우 알림이 발생하지 않습니다. **테스트 시 Discord 창을 최소화해 주세요.**

```

```