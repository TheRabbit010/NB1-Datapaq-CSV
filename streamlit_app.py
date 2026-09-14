import re
import pandas as pd

# 1. กำหนดลำดับ Probe ตามแม่แบบจริง (PB#8 ต่อจาก PB#3)
PROBE_ORDER = [
    "PB#1",
    "PB#2",
    "PB#3",
    "PB#8",
    "PB#4",
    "PB#5",
    "PB#6",
    "PB#7",
]

# 2. Map ชื่อคอลัมน์จาก Raw CSV ให้เป็นชื่อมาตรฐาน
COLUMN_MAPPING = {
    "Brazing": "Max_Temp_Brazing",
    "Debinder": "Max_Temp_Debinder",
    "Dryer": "Max_Temp_Dryer",
    "Dwell Time Above 600°C": "Dwell_600C",
    "Dwell Time Above 583°C": "Dwell_583C",
    "Dwell Time Above 577°C": "Dwell_577C",
    "Dwell Time Above 200°C": "Dwell_200C",
    "Dwell Time Above 175°C": "Dwell_175C",
}


def clean_time_format(val):
    """ปรับฟอร์แมตเวลา hh:mm:ss หรือ mm:ss ให้เป็น h:mm:ss หรือ m:ss มาตรฐาน"""
    if pd.isna(val):
        return "0:00:00"
    val_str = str(val).strip()

    # ตัดชั่วโมงตัวนำหน้าที่เป็น 00: ออกหากต้องการฟอร์แมต H:MM:SS
    if re.match(r"^00:\d{2}:\d{2}$", val_str):
        return val_str[1:]  # เปลี่ยน 00:03:36 เป็น 0:03:36
    return val_str


def process_dataset(filepath, position_type="Bottom/Top"):
    """อ่านไฟล์และจัดเรียงข้อมูลให้ตรงตามแม่แบบแบบ 100%"""
    df = pd.read_csv(filepath)

    # ตัดช่องว่างในชื่อคอลัมน์
    df.columns = df.columns.str.strip()

    # กรองเฉพาะแถวที่เป็น Probe 1-8
    df = df[df["Probe"].isin(PROBE_ORDER)].copy()

    # เรียงลำดับ Probe ตาม PROBE_ORDER ที่กำหนดไว้คงที่
    df["Probe"] = pd.Categorical(df["Probe"], categories=PROBE_ORDER, ordered=True)
    df = df.sort_values("Probe").reset_index(drop=True)

    # เพิ่มคอลัมน์ระบุตำแหน่ง (Position)
    if position_type == "Right/Left":
        df["Position"] = ["Right"] * 4 + ["Left"] * 4
    else:
        df["Position"] = ["Bottom"] * 4 + ["Top"] * 4

    # แปลงคอลัมน์เวลาให้เป็นรูปแบบเดียวกัน
    time_cols = [col for col in df.columns if "Dwell Time" in col]
    for col in time_cols:
        df[col] = df[col].apply(clean_time_format)

    # เปลี่ยนชื่อคอลัมน์ให้ตรงตามมาตรฐาน
    df = df.rename(columns=COLUMN_MAPPING)

    return df


# --- ตัวอย่างการเรียกใช้งานกับทั้ง 3 ไฟล์ ---
df_set1 = process_dataset("Export27.csv", position_type="Right/Left")
df_set2 = process_dataset("ExportSU2_2.csv", position_type="Bottom/Top")
df_set3 = process_dataset("Export16_2.csv", position_type="Bottom/Top")

# ส่งออกเป็น Excel หรือ CSV ใหม่ที่เรียงข้อมูลตรงกันทุกชุด
df_set1.to_csv("Cleaned_Set1.csv", index=False)
df_set2.to_csv("Cleaned_Set2.csv", index=False)
df_set3.to_csv("Cleaned_Set3.csv", index=False)
