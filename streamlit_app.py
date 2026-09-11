import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import io
import re
from datetime import timedelta

# 1. ตั้งค่า Page Config
st.set_page_config(
    page_title="Recorder NB1 Debinder",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. บังคับ Dark Mode CSS และตั้งค่าตัวหนังสือปุ่มดาวน์โหลดเป็นสีขาว
st.markdown("""
    <style>
        /* ซ่อนแถบขาว Header ด้านบน */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* ตั้งค่าพื้นหลัง Dark Mode */
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background-color: #0e1117 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] {
            background-color: #161b22 !important;
        }
        .stMarkdown, h1, h2, h3, p, span, label {
            color: #ffffff !important;
        }

        /* ปุ่มเคลียร์ข้อมูลใน Sidebar */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: #21262d !important;
            color: #ffffff !important;
            border: 1px solid #F0B90B !important;
            font-weight: bold !important;
            width: 100% !important;
            padding: 8px 16px !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #F0B90B !important;
            color: #000000 !important;
        }

        /* กล่อง File Uploader */
        [data-testid="stFileUploader"] {
            background-color: #161b22 !important;
            border: 1.5px solid #F0B90B !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        [data-testid="stFileUploader"] section {
            background-color: #1c2128 !important;
            border: 1px dashed #F0B90B !important;
            border-radius: 6px !important;
        }
        [data-testid="stFileUploader"] section div, 
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section small {
            color: #e6edf3 !important;
        }

        /* การ์ดไฟล์ที่อัปโหลดแล้ว */
        [data-testid="stFileUploaderFileData"],
        [data-testid="stFileUploaderFileData"] > div,
        [data-testid="stFileUploaderFile"] {
            background-color: #21262d !important;
            border: 1px solid #F0B90B !important;
            border-radius: 6px !important;
        }
        [data-testid="stFileUploaderFileData"] *,
        [data-testid="stFileUploaderFile"] * {
            color: #ffffff !important;
            font-weight: bold !important;
        }

        /* ปรับแถบ Expander */
        [data-testid="stExpander"] {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
        }
        [data-testid="stExpander"] details summary {
            background-color: #21262d !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }
        [data-testid="stExpander"] details summary * {
            color: #ffffff !important;
        }

        /* ปรับแต่งตาราง Dataframe */
        [data-testid="stDataFrame"] {
            background-color: #161b22 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
        }
        div[data-testid="stDataFrame"] div[role="grid"] {
            background-color: #161b22 !important;
            color: #ffffff !important;
        }
        div[data-testid="stDataFrame"] div[role="columnheader"] {
            background-color: #21262d !important;
            color: #ffffff !important;
        }

        /* ปรับแต่งกล่องพิมพ์ข้อความ (Text Input) */
        div[data-baseweb="input"] {
            background-color: #21262d !important;
            border: 1px solid #30363d !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }
        div[data-baseweb="input"] input {
            background-color: #21262d !important;
            color: #ffffff !important;
        }

        /* ปรับแต่งปุ่มดาวน์โหลด Excel */
        div.stDownloadButton > button {
            background-color: #21262d !important;
            border: 1.5px solid #F0B90B !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease-in-out;
        }
        div.stDownloadButton > button, 
        div.stDownloadButton > button *,
        div.stDownloadButton > button p,
        div.stDownloadButton > button span {
            color: #ffffff !important;
            font-weight: bold !important;
            font-size: 15px !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #F0B90B !important;
            border-color: #F0B90B !important;
        }
        div.stDownloadButton > button:hover,
        div.stDownloadButton > button:hover *,
        div.stDownloadButton > button:hover p,
        div.stDownloadButton > button:hover span {
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. แสดงชื่อโปรแกรมหลัก
st.title("🏭 Recorder NB1 Debinder")

# 4. ฟังก์ชันคำนวณเวลา Elapsed Time จาก Interval (00:00:01)
def format_seconds_to_time(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# 5. ฟังก์ชันอ่านไฟล์ CSV และคำนวณเวลาแกน X ตาม Interval
def parse_single_file(uploaded_file):
    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()
    
    text_content = None
    for enc in ['utf-8', 'cp932', 'shift_jis', 'tis-620', 'latin1']:
        try:
            text_content = raw_bytes.decode(enc)
            break
        except Exception:
            continue
            
    if text_content is None:
        text_content = raw_bytes.decode('utf-8', errors='ignore')

    lines = text_content.splitlines()
    
    interval_sec = 1
    start_sec = 0
    probe_labels = {}
    data_rows = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        # อ่านค่า Metadata ใน Header
        if line_str.startswith("#"):
            if "interval" in line_str:
                val = line_str.split("=")[-1].strip().rstrip(",")
                parts = val.split(":")
                if len(parts) == 3:
                    interval_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            elif "start time" in line_str and "paqfile" not in line_str:
                val = line_str.split("=")[-1].strip().rstrip(",")
                parts = val.split(":")
                if len(parts) == 3:
                    start_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
            else:
                m = re.match(r"^#(\d+)\s*=\s*(.*),?", line_str)
                if m:
                    ch_num = int(m.group(1))
                    ch_label = m.group(2).strip().rstrip(",")
                    probe_labels[ch_num] = ch_label
        else:
            parts = [p.strip() for p in line_str.split(",") if p.strip() != ""]
            if len(parts) >= 8:
                try:
                    vals = [float(p) for p in parts[:8]]
                    data_rows.append(vals)
                except ValueError:
                    continue

    if not data_rows:
        return pd.DataFrame()

    parsed_data = []
    for idx, row_vals in enumerate(data_rows):
        current_total_sec = start_sec + (idx * interval_sec)
        time_str = format_seconds_to_time(current_total_sec)
        
        row_dict = {
            "ElapsedSeconds": current_total_sec,
            "Time (HH:MM:SS)": time_str
        }
        
        for i in range(1, 9):
            col_label = f"Probe #{i}"
            if i in probe_labels:
                col_label = f"Probe #{i}: {probe_labels[i][:15]}..." if len(probe_labels[i]) > 15 else f"Probe #{i}: {probe_labels[i]}"
            row_dict[col_label] = row_vals[i-1]
            
        parsed_data.append(row_dict)

    return pd.DataFrame(parsed_data)

def process_multiple_files(uploaded_files):
    combined_dfs = []
    for file in uploaded_files:
        df_single = parse_single_file(file)
        if not df_single.empty:
            combined_dfs.append(df_single)
            
    if not combined_dfs:
        return pd.DataFrame()

    full_df = pd.concat(combined_dfs, ignore_index=True)
    full_df = full_df.sort_values("ElapsedSeconds").reset_index(drop=True)
    return full_df

# ฟังก์ชันแปลง DataFrame เป็น Binary สำหรับดาวน์โหลดเป็นไฟล์ Excel (.xlsx)
def to_excel_bytes(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = dataframe.copy()
        df_export.to_excel(writer, index=False, sheet_name='Debinder Data')
    output.seek(0)
    return output.getvalue()

# 6. เมนู Sidebar
st.sidebar.header("📁 เมนูอัปโหลดข้อมูล")

if st.sidebar.button("🧹 เคลียร์ข้อมูลไฟล์เก่าทั้งหมด"):
    st.cache_data.clear()
    st.rerun()

uploaded_files = st.sidebar.file_uploader(
    "อัปโหลดไฟล์ CSV (.csv) ได้มากกว่า 1 ไฟล์", 
    type=["csv"],
    accept_multiple_files=True
)

# 7. แสดงผลกราฟและปุ่มเลือกดาวน์โหลด Excel
if uploaded_files:
    raw_df = process_multiple_files(uploaded_files)
    
    if raw_df.empty:
        st.error("⚠️ ไม่สามารถอ่านข้อมูลจากไฟล์ที่อัปโหลดได้ กรุณาตรวจสอบว่าเป็นไฟล์ CSV จาก Recorder หรือไม่")
    else:
        st.sidebar.success(f"รวมข้อมูลสำเร็จ {len(uploaded_files)} ไฟล์ ({len(raw_df)} แถว)")

        st.sidebar.markdown("---")
        st.sidebar.header("🎛️ Dynamic Controls")
        
        # ตัวเลือกแกน X
        x_axis_mode = st.sidebar.radio(
            "📍 เลือกแกน X (X-Axis Mode):",
            ["Time (Interval = 00:00:01)", "Distance (m / mm) - Coming Soon"],
            index=0
        )
        
        min_sec = int(raw_df["ElapsedSeconds"].min())
        max_sec = int(raw_df["ElapsedSeconds"].max())
        
        selected_sec_range = st.sidebar.slider(
            "⏱️ ช่วงเวลา (Elapsed Time):",
            min_value=min_sec,
            max_value=max_sec,
            value=(min_sec, max_sec),
            format="%d s"
        )
        
        st.sidebar.caption(f"ช่วงที่เลือก: `{format_seconds_to_time(selected_sec_range[0])}` ถึง `{format_seconds_to_time(selected_sec_range[1])}`")

        df = raw_df[(raw_df["ElapsedSeconds"] >= selected_sec_range[0]) & (raw_df["ElapsedSeconds"] <= selected_sec_range[1])].copy()

        st.subheader("📊 Debinder 8-Probe Temperature Monitor (X-Axis: Interval = 00:00:01)")

        # สร้างกราฟ Plotly
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        # พาเลทสีสว่างสำหรับ 8 Probes
        probe_colors = [
            "#FF3333",  # Probe 1 - Red
            "#FF8C00",  # Probe 2 - Dark Orange
            "#FFD700",  # Probe 3 - Gold
            "#00FF66",  # Probe 4 - Lime Green
            "#00FFFF",  # Probe 5 - Cyan
            "#1E90FF",  # Probe 6 - Dodger Blue
            "#9932CC",  # Probe 7 - Dark Orchid
            "#FF1493"   # Probe 8 - Deep Pink
        ]

        # กำหนด Column แกน X
        x_data = df["Time (HH:MM:SS)"]
        x_title = "Time (HH:MM:SS) [Interval: 00:00:01]"

        if "Distance" in x_axis_mode and "Distance" in df.columns:
            x_data = df["Distance"]
            x_title = "Distance"

        # ดึง คอลัมน์ Probe ทั้ง 8
        probe_cols = [c for c in df.columns if c.startswith("Probe #")]
        for idx, col in enumerate(probe_cols[:8]):
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=df[col],
                    name=col,
                    mode="lines",
                    line=dict(color=probe_colors[idx % len(probe_colors)], width=2)
                )
            )

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#161b22",
            paper_bgcolor="#0e1117",
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                font=dict(color="#FFFFFF", size=11, family="Arial Bold"),
                bgcolor="rgba(27, 31, 36, 0.95)",
                bordercolor="#F0B90B",
                borderwidth=1.5,
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.05
            ),
            xaxis=dict(
                title=dict(text=x_title, font=dict(color="#FFFFFF", size=12)),
                tickfont=dict(color="#CCCCCC", size=10),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                linecolor="#555555"
            ),
            yaxis=dict(
                title=dict(text="Temperature (°C)", font=dict(color="#FFFFFF", size=12)),
                tickfont=dict(color="#CCCCCC", size=10),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False,
                linecolor="#555555",
                range=[0, 650]  # Scale 0 - 650 °C
            ),
            height=550,
            margin=dict(l=60, r=220, t=30, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ส่วนตรวจสอบและเลือกดาวน์โหลด Excel (.xlsx)
        with st.expander("📋 ตรวจสอบและเลือกดาวน์โหลดตารางข้อมูล Excel (.xlsx)"):
            st.dataframe(df)
            
            st.markdown("---")
            st.markdown("##### 📥 ตัวเลือกการดาวน์โหลดไฟล์ Excel")
            
            col_opt1, col_opt2 = st.columns([2, 1])
            with col_opt1:
                custom_filename = st.text_input(
                    "ตั้งชื่อไฟล์ดาวน์โหลด:", 
                    value="debinder_8probes_interval_data.xlsx"
                )
                if not custom_filename.endswith('.xlsx'):
                    custom_filename += '.xlsx'
                    
            with col_opt2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                excel_bytes = to_excel_bytes(df)
                st.download_button(
                    label="📊 ดาวน์โหลดไฟล์ Excel",
                    data=excel_bytes,
                    file_name=custom_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

else:
    st.info("👈 กรุณาเลือกอัปโหลดไฟล์ (.csv) ที่เมนูด้านซ้าย สามารถเลือกอัปโหลดได้มากกว่า 1 ไฟล์")
