import os
import pandas as pd
from supabase import create_client, Client

# إعدادات الاتصال بقاعدة البيانات السحابية (Supabase)
URL = "https://zhfyxolklugpiemhrlpz.supabase.co"
KEY = "sb_publishable_1B5zvn8xJa-H6wPDsuydcG_X-uG0dTj"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    print(f"خطأ في تهيئة الاتصال: {e}")

def save_score(student_name: str, score: int, subject: str = "General"):
    """
    دالة لحفظ نتيجة الطالب في قاعدة البيانات
    """
    try:
        data = {
            "Student Name": student_name,
            "score": score,
            "Subject": subject
        }
        response = supabase.table("Students Scores").insert(data).execute()
        return True, "تم حفظ النتيجة بنجاح!"
    except Exception as e:
        return False, f"خطأ في الحفظ: {e}"

def get_leaderboard():
    """
    دالة لجلب جدول الأوائل مرتباً تنازلياً حسب الدرجات
    """
    try:
        response = supabase.table("Students Scores").select("*").order("score", desc=True).execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame()