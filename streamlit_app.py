import pandas as pd
import numpy as np

def calculate_exact_dwell_time(df, temp_col, time_col, threshold):
    """
    คำนวณ Dwell Time (วินาที) ที่อุณหภูมิ >= threshold 
    โดยใช้ Linear Interpolation เพื่อหาจุดตัดเวลาที่แม่นยำที่สุด
    """
    # เรียงลำดับเวลาให้ถูกต้อง
    df = df.sort_values(by=time_col).reset_index(drop=True)
    
    times = df[time_col].to_numpy(dtype=float)
    temps = df[temp_col].to_numpy(dtype=float)
    
    # ตรวจสอบว่ามีข้อมูลสูงกว่า threshold หรือไม่
    above_mask = temps >= threshold
    if not np.any(above_mask):
        return 0.0
    
    crossing_times = []
    
    # หาจุดตัดขอบขาขึ้น (Rising Edge) และขาลง (Falling Edge)
    for i in range(len(temps) - 1):
        t1, t2 = times[i], times[i+1]
        T1, T2 = temps[i], temps[i+1]
        
        # เมื่อกราฟอุณหภูมิข้ามเส้น threshold
        if (T1 < threshold <= T2) or (T1 >= threshold > T2):
            if T2 != T1:
                # สูตร Linear Interpolation หาเวลา t ที่ T = threshold
                t_cross = t1 + (threshold - T1) * (t2 - t1) / (T2 - T1)
            else:
                t_cross = t1
            crossing_times.append(t_cross)
            
    # กรณีพบจุดตัดเข้าและออกครบ
    if len(crossing_times) >= 2:
        dwell_seconds = crossing_times[-1] - crossing_times[0]
    else:
        # หากจุดแรกเริ่มต้นเหนือ threshold อยู่แล้ว หรือจบขณะยังสูงกว่า threshold
        above_times = times[above_mask]
        dwell_seconds = above_times[-1] - above_times[0]
        
    return dwell_seconds

def format_dwell_time(seconds):
    """แปลงวินาทีเป็นฟอร์แมต MM:SS พร้อมปัดเศษแบบสากล"""
    seconds_rounded = int(np.round(seconds))
    minutes = seconds_rounded // 60
    secs = seconds_rounded % 60
    return f"{minutes:02d}:{secs:02d}"

# ---------------------------------------------------------
# ตัวอย่างการใช้งานกับ DataFrame
# ---------------------------------------------------------
# seconds = calculate_exact_dwell_time(df, temp_col='PB#1', time_col='Time_Sec', threshold=200.0)
# formatted_time = format_dwell_time(seconds)
