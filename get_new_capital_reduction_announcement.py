'''
查詢公告快易查網站，關鍵字為"減資"，並將新公告發送通知
'''

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from datetime import datetime, timedelta, timezone


# 台灣證券交易所公告網址
announcement_url = "https://mopsov.twse.com.tw/mops/web/ezsearch_query"


def get_sii_announcement():
    today = datetime.now().strftime('%Y%m%d')

    # 上市公司公告參數
    announcement_body = f'step=00&RADIO_CM=1&TYPEK=sii&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT=%E6%B8%9B%E8%B3%87&SDATE={today}&EDATE=&lang=TW&AN='

    # 建立有 retry 的 session
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[502, 503, 504],
        allowed_methods=["POST"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.post(announcement_url, data=announcement_body, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"連線失敗：{e}")
        return {"data": [], "message": [f"連線失敗：{e}"], "status": "fail"}
    
    # 取得公告資訊
    # response = requests.post(announcement_url, data=announcement_body)

    if response.status_code == 200:
        # 移除 UTF-8 BOM
        json_data = response.text.lstrip('\ufeff')
        # 將 JSON 資料轉換為 Python dict
        response_dict = json.loads(json_data)

        # 篩選出 'CDATE' 和 'CTIME' 與現在時間相差一小時以內的資料
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        print(f"SII one_hour_ago = {one_hour_ago}")
        filtered_data = []
        for announcement in response_dict.get("data", []):
            print(f"SII announcement = {announcement}")
            try:
                # 將 CDATE 轉換為西元年格式
                cdate_parts = announcement['CDATE'].split('/')
                year = int(cdate_parts[0]) + 1911  # 將民國年轉換為西元年
                month = cdate_parts[1]
                day = cdate_parts[2]
                converted_cdate = f"{year}-{month}-{day}"

                # 組合 'CDATE' 和 'CTIME' 成 full_time（台灣時間）
                full_time_taiwan = datetime.strptime(f"{converted_cdate} {announcement['CTIME']}", '%Y-%m-%d %H:%M:%S')

                # 將台灣時間轉換為 UTC 時間並添加時區資訊
                taiwan_offset = timedelta(hours=8)
                full_time_utc = (full_time_taiwan - taiwan_offset).replace(tzinfo=timezone.utc)

                print(f"SII full_time_taiwan = {full_time_taiwan}")
                print(f"SII full_time_utc = {full_time_utc}")

                if full_time_utc >= one_hour_ago:
                    filtered_data.append(announcement)
                    print(f"一小時內的SII announcement = {announcement}")
            except ValueError as e:
                # 如果時間格式不正確，跳過該公告
                print(f"時間格式不正確: {e}")
                continue

        response_dict["data"] = filtered_data
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}


def get_otc_announcement():
    today = datetime.now().strftime('%Y%m%d')

    # 上市公司公告參數
    announcement_body = f'step=00&RADIO_CM=1&TYPEK=otc&CO_MARKET=&CO_ID=&PRO_ITEM=&SUBJECT=%E6%B8%9B%E8%B3%87&SDATE={today}&EDATE=&lang=TW&AN='

    # 建立有 retry 的 session
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[502, 503, 504],
        allowed_methods=["POST"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.post(announcement_url, data=announcement_body, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"連線失敗：{e}")
        return {"data": [], "message": [f"連線失敗：{e}"], "status": "fail"}
    
    # 取得公告資訊
    # response = requests.post(announcement_url, data=announcement_body)

    if response.status_code == 200:
        # 移除 UTF-8 BOM
        json_data = response.text.lstrip('\ufeff')
        # 將 JSON 資料轉換為 Python dict
        response_dict = json.loads(json_data)

        # 篩選出 'CDATE' 和 'CTIME' 與現在時間相差一小時以內的資料
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        print(f"OTC one_hour_ago = {one_hour_ago}")
        filtered_data = []
        for announcement in response_dict.get("data", []):
            print(f"OTC announcement = {announcement}")
            try:
                # 將 CDATE 轉換為西元年格式
                cdate_parts = announcement['CDATE'].split('/')
                year = int(cdate_parts[0]) + 1911  # 將民國年轉換為西元年
                month = cdate_parts[1]
                day = cdate_parts[2]
                converted_cdate = f"{year}-{month}-{day}"

                # 組合 'CDATE' 和 'CTIME' 成 full_time（台灣時間）
                full_time_taiwan = datetime.strptime(f"{converted_cdate} {announcement['CTIME']}", '%Y-%m-%d %H:%M:%S')

                # 將台灣時間轉換為 UTC 時間並添加時區資訊
                taiwan_offset = timedelta(hours=8)
                full_time_utc = (full_time_taiwan - taiwan_offset).replace(tzinfo=timezone.utc)

                print(f"OTC full_time_taiwan = {full_time_taiwan}")
                print(f"OTC full_time_utc = {full_time_utc}")

                if full_time_utc >= one_hour_ago:
                    filtered_data.append(announcement)
                    print(f"一小時內的OTC announcement = {announcement}")
            except ValueError as e:
                # 如果時間格式不正確，跳過該公告
                print(f"時間格式不正確: {e}")
                continue

        response_dict["data"] = filtered_data
        return response_dict
    return {"data": [], "message": ["查無公告資料"], "status": "fail"}


def check_new_announcements():
    sii_response_dict = get_sii_announcement()
    otc_response_dict = get_otc_announcement()

    new_announcements = sii_response_dict["data"] + otc_response_dict["data"]
    
    if new_announcements:
        # 處理新公告，例如發送通知
        print("有新的公告：")
        for announcement in new_announcements:
            announcement_details = f"{announcement['CDATE']}\n{announcement['COMPANY_ID']}{announcement['COMPANY_NAME']}\n{announcement['SUBJECT']}\n{announcement['HYPERLINK']}"
            print(announcement_details)
        
    else:
        print("沒有新的公告")

    return new_announcements


if __name__ == "__main__":
    check_new_announcements()





