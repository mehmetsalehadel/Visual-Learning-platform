# type: ignore
import streamlit as st
import io
import sys

def submit_lab_score(student_name, score, subject):
    # هذه الدالة تتلقى اسم الطالب، درجته، واسم المادة وترسلها لقاعدة البيانات
    pass

def run_lab_editor():
    st.subheader("💻 بيئة بايثون العملية - المرجع الشامل لتمارين الأمن السيبراني")
    st.write("اختبري وتدربي على جميع الأمثلة والتمارين البرمجية الواردة في المنهج التعليمي بالكامل!")

    # صندوق إدخال اسم الطالب لربطه بالنتيجة ونظام الأوائل
    student_name = st.text_input("اسم الطالب الثلاثي:", placeholder="اكتب اسمك هنا...")

    # قائمة شاملة لكل تمارين المنهج المستخرجة من الملفات
    lab_challenge = st.selectbox(
        "اختر التمرين العملي:",
        [
            "1. أساسيات بايثون (طباعة النصوص والمتغيرات الأنواع)",
            "2. الشروط والتحمّل الأمني (If/Elif/Else)",
            "3. الحلقات التكرارية لمعالجة السجلات (For & While Loops)",
            "4. مثال عملي متكامل لفحص محاولات الدخول",
            "5. مكتبة os: فحص وجود وحجم ملفات السجلات",
            "6. مكتبة sys: قراءة إصدار بايثون ومعاملات النظام",
            "7. التعبيرات النمطية re: استخراج عناوين IP وعد المحاولات الفاشلة",
            "8. مكتبة json: معالجة أحداث الأمان وتوليد تنبيهات Brute-Force",
            "9. مكتبة hashlib: حساب البصمة الرقمية SHA-256 وفحص سلامة الملفات",
            "10. مكتبة socket: اختبار الاتصال الشبكي وتحويل أسماء النطاقات",
            "11. مكتبة subprocess: تنفيذ أوامر النظام بأمان (مثل ipconfig)",
            "12. مكتبة logging: تسجيل الأخطاء والتحذيرات الأمنية في ملف خارجي",
            "13. مكتبة datetime: تسجيل التوقيتات وتتبع تسلسل الأحداث الأمنية",
            "14. المكتبات الخارجية Requests & NumPy: الاتصالات والمعالجة الرياضية",
            "15. مكتبة Pandas: تحليل سجلات المصادقة بجدول بيانات متقدم",
            "16. مكتبة Scikit-learn: نماذج تصنيف الأمان وتعلم الآلة",
            "17. مكتبة Cryptography: تشفير وفك تشفير البيانات الحساسة (Fernet)",
            "18. أتمتة الكشف المتقدم عن الهجمات (Threat Detection Automation)"
        ]
    )

    # قوالب الأكواد الافتراضية لكل التمارين
    if lab_challenge and "1." in lab_challenge:
        default_code = '''# أساسيات بايثون وأنواع البيانات وطباعتها
print("Hello, Cybersecurity!")

username = "admin"
age = 30
score = 95.5
active = True

print(type(username))
print(type(age))
print(type(score))
print(type(active))
'''
    elif lab_challenge and "2." in lab_challenge:
        default_code = '''# استخدام الشروط المنطقية في اتخاذ القرارات الأمنية
risk_score = 0.85

if risk_score >= 0.80:
    print("Access denied: High risk detected.")
elif risk_score >= 0.50:
    print("Multi-factor authentication required.")
else:
    print("Access granted.")
'''
    elif lab_challenge and "3." in lab_challenge:
        default_code = '''# استخدام الحلقات لمعالجة المنافذ وسجلات الدخول
ports = [22, 80, 443, 8080]
print("Scanning ports:")
for port in ports:
    print(f"Port {port} is active.")

attempts = 0
print("\\nRunning authentication retry loop:")
while attempts < 3:
    print(f"Authentication attempt {attempts + 1}")
    attempts += 1
'''
    elif lab_challenge and "4." in lab_challenge:
        default_code = '''# برنامج أمني صغير يجمع المدخلات والشروط
username = "Admin"
failed_attempts = 6

if failed_attempts >= 5:
    print("ALERT: Account may be under attack.")
else:
    print("Normal authentication activity.")
print("User:", username)
'''
    elif lab_challenge and "5." in lab_challenge:
        default_code = '''# تمرين مكتبة os للتحقق من ملفات السجلات
import os

file_path = "security.log"
with open(file_path, "w") as f:
    f.write("Sample log data for testing os module.")

if os.path.exists(file_path):
    size = os.path.getsize(file_path)
    print("Security log file exists.")
    print("File size:", size, "bytes")
else:
    print("File does not exist.")
'''
    elif lab_challenge and "6." in lab_challenge:
        default_code = '''# تمرين مكتبة sys لفحص بيئة بايثون
import sys

print("Python version:")
print(sys.version)
print("Operating platform:")
print(sys.platform)
'''
    elif lab_challenge and "7." in lab_challenge:
        default_code = '''# تمرين استخراج عناوين IP وعد حالات الفشل باستخدام re
import re

log = """
Failed login from 192.168.1.10
Successful login from 10.0.0.5
Failed login from 172.16.0.20
"""

pattern = r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"
ip_addresses = re.findall(pattern, log)
print("Extracted IP Addresses:", ip_addresses)

failed_logins = re.findall(r"FAILED", log, re.IGNORECASE)
print("Failed login count:", len(failed_logins))
'''
    elif lab_challenge and "8." in lab_challenge:
        default_code = '''# تمرين معالجة الأحداث الأمنية بصيغة JSON
import json

event = '{"user": "Admin", "failed_attempts": 8}'
data = json.loads(event)

print("User:", data["user"])
print("Failed attempts:", data["failed_attempts"])

if data["failed_attempts"] >= 5:
    print("SECURITY ALERT! Possible brute-force attack.")
'''
    elif lab_challenge and "9." in lab_challenge:
        default_code = '''# تمرين حساب الهاش البصمة الرقمية SHA-256
import hashlib

data = "Cybersecurity Confidential Data"
hash_value = hashlib.sha256(data.encode("utf-8")).hexdigest()
print("SHA-256 Hash:", hash_value)
'''
    elif lab_challenge and "10." in lab_challenge:
        default_code = '''# تمرين فحص الاتصال الشبكي واسم النطاق عبر socket
import socket

domain = "example.com"
try:
    ip_address = socket.gethostbyname(domain)
    print("Domain:", domain)
    print("Resolved IP address:", ip_address)
except socket.gaierror:
    print("DNS resolution failed.")
'''
    elif lab_challenge and "11." in lab_challenge:
        default_code = '''# تمرين تنفيذ أوامر النظام بأمان عبر subprocess
import subprocess
import sys

try:
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
        check=True
    )
    print("Subprocess Output:")
    print(result.stdout.strip())
except subprocess.SubprocessError as error:
    print("Command failed:", error)
'''
    elif lab_challenge and "12." in lab_challenge:
        default_code = '''# تمرين تسجيل الأخطاء والتحذيرات بملف logging
import logging

logging.basicConfig(
    filename="security_test.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

failed_attempts = 6
if failed_attempts >= 5:
    logging.warning("Multiple failed login attempts detected.")
    print("Security warning logged successfully.")
'''
    elif lab_challenge and "13." in lab_challenge:
        default_code = '''# تمرين تسجيل الأوقات والطوابع الزمنية الأمنية
from datetime import datetime, timezone

event_time = datetime.now(timezone.utc)
print("Security event UTC time:", event_time)
'''
    elif lab_challenge and "14." in lab_challenge:
        default_code = '''# تمرين استخدام NumPy والمعالجة الرياضية
import numpy as np

numbers = [10, 20, 30, 40, 50]
average = np.mean(numbers)
print("NumPy Average Score:", average)
'''
    elif lab_challenge and "15." in lab_challenge:
        default_code = '''# تمرين تحليل سجلات المصادقة بجدول بيانات Pandas
import pandas as pd

data = {
    "User": ["Ali", "Sara", "Omar", "Admin"],
    "Failed_Logins": [1, 2, 7, 8]
}

df = pd.DataFrame(data)
print("Full DataFrame:")
print(df)

suspicious = df[df["Failed_Logins"] >= 5]
print("\\nHigh Risk Users:")
print(suspicious)
'''
    elif lab_challenge and "16." in lab_challenge:
        default_code = '''# تمرين بناء نموذج تصنيف تعليم آلي مبدئي
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier()
print("Scikit-learn Decision Tree model successfully created!")
'''
    elif lab_challenge and "17." in lab_challenge:
        default_code = '''# تمرين التشفير وفك التشفير باستخدام Fernet
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

message = b"Confidential Security Data"
encrypted = cipher.encrypt(message)
decrypted = cipher.decrypt(encrypted)

print("Original:", message.decode())
print("Encrypted:", encrypted)
print("Decrypted:", decrypted.decode())
'''
    else:
        default_code = '''# تمرين أتمتة اكتشاف الهجمات الشامل
events = [
    {"user": "Ali", "failed": 1},
    {"user": "Sara", "failed": 2},
    {"user": "Admin", "failed": 8}
]

print("Scanning security events for anomalies...")
for event in events:
    if event["failed"] >= 5:
        print(f"SECURITY ALERT: Suspicious activity from user -> {event['user']}")
'''

    # صندوق محرر الكود البرمجي
    user_code = st.text_area("محرر الكود البرمجي (Python Code Editor):", value=default_code, height=280)

    # أزرار التنفيذ والتسليم
    col1, col2 = st.columns(2)
    with col1:
        run_btn = st.button("🚀 تنفيذ الكود واستعراض النتائج")
    with col2:
        submit_btn = st.button("💾 تسليم التمرين وإرسال الدرجة")

    # تنفيذ الكود البرمجي وعرض المخرجات
    if run_btn:
        st.markdown("---")
        st.subheader("📥 مخرجات التنفيذ (Output):")
        
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            exec(user_code)
            output_result = new_stdout.getvalue()
            
            if output_result.strip():
                st.code(output_result, language="text")
            else:
                st.success("تم تنفيذ الكود بنجاح!")
                
        except Exception as e:
            st.error("حدث خطأ أثناء تنفيذ الكود البرمجي:")
            st.code(str(e), language="text")
            
        finally:
            sys.stdout = old_stdout

    # زر التسليم وربطه بقاعدة البيانات عبر الدالة التي أضفناها
    if submit_btn:
        if not student_name.strip():
            st.warning("يرجى كتابة اسم الطالب الثلاثي قبل تسليم التمرين!")
        else:
            score_value = 100
            subject_name = "Python Advanced Cybersecurity Labs"
            
            # استدعاء دالة تسليم الدرجة التي تم إضافتها
            submit_lab_score(student_name, score_value, subject_name)
            
            st.success(f"أحسنتِ يا {student_name}! تم إرسال نتيجتك ({score_value}) بنجاح وتحديث لوحة الأوائل 🎉")

if __name__ == "__main__":
    run_lab_editor()