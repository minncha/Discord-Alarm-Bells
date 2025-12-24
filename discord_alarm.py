import asyncio
import datetime
import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext

import pystray
import requests
from PIL import Image
from winsdk.windows.ui.notifications import NotificationKinds
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus

# ==========================================
# [사용자 설정]
# ==========================================
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"
TARGET_APP_KEYWORD = "Discord"
ICON_FILE_NAME = "bells.ico"
# ==========================================

def resource_path(relative_path):
    """ EXE 실행 시 임시 폴더에 풀리는 리소스 경로를 찾기 위한 함수 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class NotificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Notifier")
        self.root.geometry("300x100")
        self.root.resizable(False, False)

        # 닫기 버튼(X) 클릭 시 트레이로 숨기기 설정
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # UI 구성
        self.status_label = tk.Label(root, text="[시스템 트레이 모드 대기 중]", fg="blue", font=("맑은 고딕", 10, "bold"))
        self.status_label.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=50, height=12, state='disabled', font=("맑은 고딕", 9))
        self.log_area.pack(padx=10, pady=5)

        self.is_running = True
        self.tray_icon = None

        # 모니터링 시작
        self.start_monitoring_thread()

        # 트레이 아이콘 초기화 (백그라운드 스레드에서 실행)
        self.setup_tray_icon()

    def minimize_to_tray(self):
        """윈도우 창을 숨깁니다 (프로그램 종료 X)"""
        self.root.withdraw()
        if self.tray_icon:
            self.tray_icon.notify("백그라운드에서 실행 중입니다.", "Discord Notifier")

    def show_window(self):
        """숨겨진 창을 다시 띄웁니다"""
        self.root.deiconify()
        self.root.lift()

    def quit_app(self):
        """프로그램 완전 종료"""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit()

    def setup_tray_icon(self):
        """시스템 트레이 아이콘 생성"""
        try:
            # 아이콘 이미지 로드 (EXE 내부 경로 대응)
            image_path = resource_path(ICON_FILE_NAME)
            image = Image.open(image_path)

            # 메뉴 생성 (열기, 종료)
            menu = pystray.Menu(
                pystray.MenuItem("열기", lambda: self.root.after(0, self.show_window), default=True),
                pystray.MenuItem("종료", lambda: self.root.after(0, self.quit_app))
            )

            self.tray_icon = pystray.Icon("DiscordNotifier", image, "Discord Notifier", menu)

            # 트레이 아이콘은 별도 스레드에서 실행해야 GUI가 안 멈춤
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

        except Exception as e:
            self.log(f"트레이 아이콘 오류: {e}")

    # --- 기존 로직 (로그, 전송, 모니터링) ---
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        full_msg = f"[{timestamp}] {message}"
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, full_msg + "\n")

        if int(self.log_area.index('end-1c').split('.')[0]) > 50:
            self.log_area.delete("1.0", "2.0")

        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def update_status(self, text, color="black"):
        self.status_label.config(text=text, fg=color)

    def send_telegram(self, title, message):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": f"🔔 <b>[{title}]</b>\n{message}", "parse_mode": "HTML"}
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass

    def start_monitoring_thread(self):
        thread = threading.Thread(target=self.run_async_loop)
        thread.daemon = True
        thread.start()

    def run_async_loop(self):
        asyncio.run(self.main_logic())

    async def main_logic(self):
        try:
            try:
                listener = UserNotificationListener.current
            except AttributeError:
                listener = UserNotificationListener.get_current()

            if not listener: return
            if await listener.request_access_async() != UserNotificationListenerAccessStatus.ALLOWED:
                self.update_status("권한 없음", "red")
                return

            self.update_status("● 모니터링 중 (트레이 모드)", "green")
            processed_ids = set()

            while self.is_running:
                notifications = await listener.get_notifications_async(NotificationKinds.TOAST)
                current_ids = set()

                for notif in notifications:
                    n_id = notif.id
                    current_ids.add(n_id)
                    if n_id in processed_ids: continue

                    try:
                        app_name = notif.app_info.display_info.display_name
                        if TARGET_APP_KEYWORD.lower() in app_name.lower():
                            texts = notif.notification.visual.bindings[0].get_text_elements()
                            extracted = [t.text for t in texts]
                            title = extracted[0] if extracted else "알림"
                            body = " ".join(extracted[1:]) if len(extracted) > 1 else ""

                            self.log(f"{body[:15]}...")
                            self.send_telegram(app_name, body)
                    except:
                        pass
                    processed_ids.add(n_id)

                processed_ids = processed_ids.intersection(current_ids)
                await asyncio.sleep(5.0)  # CPU 최적화 유지

        except Exception as e:
            self.log(f"Error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NotificationApp(root)
    root.mainloop()
