import schedule
import time
import threading
import signal
import sys
import requests


from get_new_capital_reduction_announcement import check_new_announcements  # 匯入函式


def notify_discord_webhook(msg):
    url = 'https://discord.com/api/webhooks/1326823867993292925/HGjb1m3D1bQAWHxIIpsx7AGqhEN3km-AwIKD3L3t8opjhcMpUHKK_PnAYoCV2FPQ-Uzf'
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "公告-減資"}
    res = requests.post(url, headers = headers, json = data) 
    if res.status_code in (200, 204):
            print(f"Request fulfilled with response: {res.text}")
    else:
            print(f"Request failed with response: {res.status_code}-{res.text}")


def generate_msg():
    new_announcements = check_new_announcements()  # 呼叫函式取得新公告
    if new_announcements:
        msg = '\n\n'.join(
            f"{announcement['CDATE']}\n{announcement['COMPANY_ID']} {announcement['COMPANY_NAME']}\n{announcement['SUBJECT']}\n{announcement['HYPERLINK']}"
            for announcement in new_announcements
        )
        return msg
    return None

def job():
    msg = generate_msg()
    if msg:
        notify_discord_webhook(msg)

# 設定每10分鐘檢查一次公告並廣播
schedule.every(10).minutes.do(job)


def run_schedule():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Error running scheduled job: {e}")
        time.sleep(1)

def signal_handler(sig, frame):
    global running
    print('Stopping the scheduler...')
    running = False
    sys.exit(0)

if __name__ == "__main__":

    job()  # 立即執行一次
    
    # 設定停止信號處理
    signal.signal(signal.SIGINT, signal_handler)

    # 初始化 running 變數
    running = True

    # 啟動定時任務的背景執行緒
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()
