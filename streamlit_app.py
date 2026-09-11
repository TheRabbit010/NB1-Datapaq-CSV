import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import io
import re

# 1. ตั้งค่า Page Config
st.set_page_config(
    page_title="Datapaq NB1",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. บังคับ Dark Mode CSS
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

        /* สไตล์กล่องแสดง Header Metadata แบบ Raw Header (#key = value) */
        .raw-header-box {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-left: 4px solid #F0B90B;
            border-radius: 6px;
            padding: 12px 18px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            color: #e6edf3;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        .raw-header-key {
            color: #58a6ff;
            font-weight: bold;
        }
        .raw-header-val {
            color: #D29922;
            font-weight: bold;
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
st.title("🏭 Datapaq NB1")

# 4. ฟังก์ชันแปลงวินาทีเป็นรูปแบบ HH:MM:SS
def format_seconds_to_time(total_seconds):
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# ฟังก์ชันแปลง Hex Color เป็น RGBA
def hex_to_rgba(hex_str, opacity=0.25):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {opacity})"

# 5. ฟังก์ชันอ่านไฟล์ CSV และดึงข้อมูล
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
    
    metadata = {
        "paqfile start date": "-",
        "paqfile start time": "-",
        "title": "-",
        "operator": "-",
        "product": "-"
    }

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        if line_str.startswith("#"):
            line_clean = line_str.lstrip("#").strip()
            if "=" in line_clean:
                key, val = [p.strip() for p in line_clean.split("=", 1)]
                val = val.rstrip(",")
                
                if key.lower() == "title":
                    metadata["title"] = val
                elif key.lower() == "paqfile start date":
                    metadata["paqfile start date"] = val
                elif key.lower() == "paqfile start time":
                    metadata["paqfile start time"] = val
                elif key.lower() == "operator":
                    metadata["operator"] = val
                elif key.lower() == "product":
                    metadata["product"] = val
                elif key.lower() == "interval":
                    parts = val.split(":")
                    if len(parts) == 3:
                        interval_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                elif key.lower() == "start time":
                    parts = val.split(":")
                    if len(parts) == 3:
                        start_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                elif key.isdigit():
                    ch_num = int(key)
                    probe_labels[ch_num] = val
        else:
            parts = [p.strip() for p in line_str.split(",") if p.strip() != ""]
            if len(parts) >= 8:
                try:
                    vals = [float(p) for p in parts[:8]]
                    data_rows.append(vals)
                except ValueError:
                    continue

    if not data_rows:
        return pd.DataFrame(), metadata

    parsed_data = []
    for idx, row_vals in enumerate(data_rows):
        current_total_sec = start_sec + (idx * interval_sec)
        time_str = format_seconds_to_time(current_total_sec)
        distance_m = current_total_sec * 0.02  # 00:00:00 = 0.0m, +0.02m per sec
        
        row_dict = {
            "ElapsedSeconds": current_total_sec,
            "Time (HH:MM:SS)": time_str,
            "Distance (m)": round(distance_m, 2)
        }
        
        for i in range(1, 9):
            col_label = f"Probe #{i}"
            if i in probe_labels:
                col_label = f"Probe #{i}: {probe_labels[i][:15]}..." if len(probe_labels[i]) > 15 else f"Probe #{i}: {probe_labels[i]}"
            row_dict[col_label] = row_vals[i-1]
            
        parsed_data.append(row_dict)

    return pd.DataFrame(parsed_data), metadata

def process_multiple_files(uploaded_files):
    combined_dfs = []
    first_metadata = None
    
    for file in uploaded_files:
        df_single, meta_single = parse_single_file(file)
        if not df_single.empty:
            combined_dfs.append(df_single)
            if first_metadata is None:
                first_metadata = meta_single
            
    if not combined_dfs:
        return pd.DataFrame(), {}

    full_df = pd.concat(combined_dfs, ignore_index=True)
    full_df = full_df.sort_values("ElapsedSeconds").reset_index(drop=True)
    return full_df, first_metadata

# ฟังก์ชันแปลง DataFrame เป็น Binary สำหรับดาวน์โหลด Excel (.xlsx)
def to_excel_bytes(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = dataframe.copy()
        df_export.to_excel(writer, index=False, sheet_name='Datapaq Data')
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

# 7. แสดงผล Header Metadata + กราฟพร้อมโซนเวลา
if uploaded_files:
    df, metadata = process_multiple_files(uploaded_files)
    
    if df.empty:
        st.error("⚠️ ไม่สามารถอ่านข้อมูลจากไฟล์ที่อัปโหลดได้ กรุณาตรวจสอบว่าเป็นไฟล์ CSV จาก Datapaq หรือไม่")
    else:
        st.sidebar.success(f"รวมข้อมูลสำเร็จ {len(uploaded_files)} ไฟล์ ({len(df)} แถว)")

        st.sidebar.markdown("---")
        st.sidebar.header("🎛️ Dynamic Controls")
        
        st.sidebar.subheader("🎨 โหมดแสดงสีพื้นหลัง (Background Shading Mode)")
        
        color_shading_mode = st.sidebar.radio(
            "เลือกโหมดแสดงสี:",
            ["แสดงสีตามโซน (By Zone)", "แสดงสีตามกลุ่มงาน (By Process Group)"],
            index=0
        )

        # กำหนดช่วงเวลาโซนคงที่
        if color_shading_mode == "แสดงสีตามโซน (By Zone)":
            zones_data = [
                {"Start Time": "00:00:00", "End Time": "00:02:14", "Zone Name": "Dryer Z#1"},
                {"Start Time": "00:02:15", "End Time": "00:04:28", "Zone Name": "Dryer Z#2"},
                {"Start Time": "00:04:29", "End Time": "00:04:58", "Zone Name": "EXT Dryer"},
                {"Start Time": "00:04:59", "End Time": "00:05:26", "Zone Name": "ENT DB"},
                {"Start Time": "00:05:27", "End Time": "00:07:41", "Zone Name": "DB Z#1"},
                {"Start Time": "00:07:42", "End Time": "00:09:32", "Zone Name": "DB Z#2"},
                {"Start Time": "00:09:33", "End Time": "00:11:23", "Zone Name": "DB Z#3"},
                {"Start Time": "00:11:24", "End Time": "00:13:38", "Zone Name": "DB Z#4"},
                {"Start Time": "00:13:39", "End Time": "00:15:34", "Zone Name": "XFER#1"},
                {"Start Time": "00:15:35", "End Time": "00:17:48", "Zone Name": "Z#1"},
                {"Start Time": "00:17:49", "End Time": "00:19:43", "Zone Name": "Z#2"},
                {"Start Time": "00:19:44", "End Time": "00:21:40", "Zone Name": "Z#3"},
                {"Start Time": "00:21:41", "End Time": "00:23:07", "Zone Name": "Z#4"},
                {"Start Time": "00:23:08", "End Time": "00:24:33", "Zone Name": "Z#5"},
                {"Start Time": "00:24:34", "End Time": "00:25:59", "Zone Name": "Z#6"},
                {"Start Time": "00:26:00", "End Time": "00:27:37", "Zone Name": "Z#7"},
                {"Start Time": "00:27:38", "End Time": "00:29:19", "Zone Name": "WatCool#1"},
                {"Start Time": "00:29:20", "End Time": "00:30:41", "Zone Name": "WatCool#2"},
                {"Start Time": "00:30:42", "End Time": "00:32:02", "Zone Name": "Exit curtain box"},
                {"Start Time": "00:32:03", "End Time": "00:32:28", "Zone Name": "XFER#2"},
                {"Start Time": "00:32:29", "End Time": "00:33:21", "Zone Name": "AirCool#1"},
                {"Start Time": "00:33:22", "End Time": "00:34:15", "Zone Name": "AirCool#2"},
                {"Start Time": "00:34:16", "End Time": "00:35:35", "Zone Name": "Exit"}
            ]
            angle_setting = -90
        else:
            zones_data = [
                {"Start Time": "00:00:00", "End Time": "00:04:58", "Zone Name": "Dryer", "Color": "#FF8C00"},      # ส้มอุ่น (~300°C)
                {"Start Time": "00:04:59", "End Time": "00:15:34", "Zone Name": "Debinder", "Color": "#E63946"},   # แดงส้ม (~350°C)
                {"Start Time": "00:15:35", "End Time": "00:27:37", "Zone Name": "Brazing", "Color": "#FF0033"},    # แดงเพลิง (~600°C)
                {"Start Time": "00:27:38", "End Time": "00:34:15", "Zone Name": "Cool", "Color": "#00B4D8"},       # ฟ้าเย็น
                {"Start Time": "00:34:16", "End Time": "00:35:35", "Zone Name": "Exit", "Color": "#6C757D"}        # เทาเย็น
            ]
            angle_setting = 0

        # 📋 แสดงผล Header Metadata
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown(f"""
                <div class="raw-header-box">
                    <div><span class="raw-header-key">#paqfile start date</span> = <span class="raw-header-val">{metadata.get('paqfile start date', '-')}</span></div>
                    <div><span class="raw-header-key">#paqfile start time</span> = <span class="raw-header-val">{metadata.get('paqfile start time', '-')}</span></div>
                    <div><span class="raw-header-key">#title</span> = <span class="raw-header-val">{metadata.get('title', '-')}</span></div>
                </div>
            """, unsafe_allow_html=True)
        with col_h2:
            st.markdown(f"""
                <div class="raw-header-box">
                    <div><span class="raw-header-key">#operator</span> = <span class="raw-header-val">{metadata.get('operator', '-')}</span></div>
                    <div><span class="raw-header-key">#product</span> = <span class="raw-header-val">{metadata.get('product', '-')}</span></div>
                </div>
            """, unsafe_allow_html=True)

        # สร้างกราฟ Plotly
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        # สี Probes ตามตาราง Datapaq (#1 ถึง #8)
        probe_colors = [
            "#FF0000",  # Probe #1 - Red
            "#00FF00",  # Probe #2 - Green
            "#0000FF",  # Probe #3 - Blue
            "#8B4513",  # Probe #4 - Brown
            "#FF00FF",  # Probe #5 - Pink / Magenta
            "#DAA520",  # Probe #6 - Golden Yellow
            "#800080",  # Probe #7 - Purple
            "#00FFFF"   # Probe #8 - Cyan
        ]

        # พาเลทสีสว่างสำหรับสลับระบายพื้นหลัง
        zone_palette = [
            "#FF9F43", "#00CEC9", "#10AC84", "#9B59B6", "#FF6B6B", 
            "#FECA57", "#48DBFB", "#FF9FF3", "#54A0FF", "#5F27CD",
            "#00D2D3", "#FF9F1A", "#2E86DE", "#EE5253", "#0ABDE3"
        ]

        # 1. Plot ข้อมูล Probe ทั้ง 8 บนแกนเวลาหลัก (Time (HH:MM:SS))
        probe_cols = [c for c in df.columns if c.startswith("Probe #")]
        for idx, col in enumerate(probe_cols[:8]):
            fig.add_trace(
                go.Scatter(
                    x=df["Time (HH:MM:SS)"],
                    y=df[col],
                    name=col,
                    mode="lines",
                    line=dict(color=probe_colors[idx % len(probe_colors)], width=2)
                )
            )

        # 🎯 2. เพิ่ม Dummy Trace เพื่อเปิดใช้งานและผูกข้อมูลกับ xaxis2 (Distance (m))
        fig.add_trace(
            go.Scatter(
                x=df["Distance (m)"],
                y=[None] * len(df),
                xaxis="x2",
                showlegend=False,
                hoverinfo="skip"
            )
        )

        # 3. วาดพื้นหลังโซนเวลา/กลุ่มงานสลับสีแบบโปร่งใส + วางชื่อโซน
        for idx, z_item in enumerate(zones_data):
            start_t = z_item["Start Time"]
            end_t = z_item["End Time"]
            z_name = z_item["Zone Name"]
            
            if "Color" in z_item:
                color_hex = z_item["Color"]
            else:
                color_hex = zone_palette[idx % len(zone_palette)]

            fill_opacity = 0.22 if color_shading_mode == "แสดงสีตามกลุ่มงาน (By Process Group)" else 0.20
            fill_rgba = hex_to_rgba(color_hex, fill_opacity)
            line_rgba = hex_to_rgba(color_hex, 0.60)
            
            fig.add_vrect(
                x0=start_t,
                x1=end_t,
                fillcolor=fill_rgba,
                layer="below",
                line_width=1.5,
                line_dash="dot",
                line_color=line_rgba
            )
            
            font_sz = 11 if color_shading_mode == "แสดงสีตามกลุ่มงาน (By Process Group)" else 9
            
            fig.add_annotation(
                x=start_t,
                y=620,
                text=f"<b>{z_name}</b>",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(color="#FFFFFF", size=font_sz, family="Arial Bold"),
                textangle=angle_setting
            )

        # คำนวณช่วง Tick Values เว้นช่วงสเกลแกนเวลาและระยะทางให้สมดุล
        step_tick = max(1, len(df) // 16)
        tick_indices = list(range(0, len(df), step_tick))
        if (len(df) - 1) not in tick_indices:
            tick_indices.append(len(df) - 1)

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
                y=0.88,
                xanchor="left",
                x=1.02
            ),
            # แกน Y หลัก
            yaxis=dict(
                title=dict(text="Temperature (°C)", font=dict(color="#FFFFFF", size=12)),
                tickfont=dict(color="#CCCCCC", size=10),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False,
                linecolor="#555555",
                domain=[0.22, 1.0],  # ย่อความสูงกราฟเพื่อเปิดพื้นที่ด้านล่างให้แกน X สองแถบ
                range=[0, 650]
            ),
            # แกน X ที่ 1 (Time (hh:mm:ss)) - แถบส่วนบน
            xaxis=dict(
                title=dict(text="Time (hh:mm:ss)", font=dict(color="#FFFFFF", size=11)),
                tickmode="array",
                tickvals=df.loc[tick_indices, "Time (HH:MM:SS)"].tolist(),
                tickfont=dict(color="#CCCCCC", size=10),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                showline=True,
                linewidth=1,
                linecolor="#888888",
                anchor="free",
                position=0.12  # ลอยอยู่ที่ความสูง y=0.12
            ),
            # แกน X ที่ 2 (Distance (m)) - แถบแยกด้านล่างสุด
            xaxis2=dict(
                title=dict(text="Distance (m)", font=dict(color="#F0B90B", size=11)),
                overlaying="x",
                anchor="free",
                position=0.00,  # อยู่ล่างสุดที่ y=0.00 แยกกรอบชัดเจน
                tickmode="array",
                tickvals=df.loc[tick_indices, "Distance (m)"].tolist(),
                ticktext=[f"{d:.2f}" for d in df.loc[tick_indices, "Distance (m)"]],
                tickfont=dict(color="#F0B90B", size=10),
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor="#F0B90B"
            ),
            height=660,
            margin=dict(l=60, r=240, t=50, b=120)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------------------------------------------------------
        # 📊 ตารางสรุปค่า (เฉพาะตัวเลขสำหรับ Copy ไปวางใน Google Sheets)
        # ---------------------------------------------------------
        st.markdown("### 📊 ตารางสรุปผลการวิเคราะห์ (Data Table for Google Sheets Copy)")

        dryer_subset = df[(df["ElapsedSeconds"] >= 0) & (df["ElapsedSeconds"] <= 298)]
        debinder_subset = df[(df["ElapsedSeconds"] >= 299) & (df["ElapsedSeconds"] <= 934)]
        brazing_subset = df[(df["ElapsedSeconds"] >= 935) & (df["ElapsedSeconds"] <= 1657)]

        def format_excel_time(seconds):
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}:{mins:02d}:{secs:02d}"

        summary_rows = []
        for col_name in probe_cols[:8]:
            # 1. Dryer Max
            d_max = round(dryer_subset[col_name].max(), 1) if not dryer_subset.empty else 0.0
            
            # 2. Debinder Max
            db_max = round(debinder_subset[col_name].max(), 1) if not debinder_subset.empty else 0.0
            
            # 3. Brazing Max & Dwell Times
            br_max = round(brazing_subset[col_name].max(), 1) if not brazing_subset.empty else 0.0
            br_dwell_577 = (brazing_subset[col_name] > 577).sum() if not brazing_subset.empty else 0
            br_dwell_583 = (brazing_subset[col_name] > 583).sum() if not brazing_subset.empty else 0
            br_dwell_600 = (brazing_subset[col_name] > 600).sum() if not brazing_subset.empty else 0

            summary_rows.append({
                "Probe Name": col_name,
                "Brazing Max (°C)": br_max,
                "Debinder Max (°C)": db_max,
                "Dryer Max (°C)": d_max,
                "at 600°C / probe": format_excel_time(br_dwell_600),
                "at 583°C / probe": format_excel_time(br_dwell_583),
                "at 577°C / probe": format_excel_time(br_dwell_577)
            })

        summary_df = pd.DataFrame(summary_rows)

        st.dataframe(summary_df, use_container_width=True)

        # คำอธิบายเกณฑ์มาตรฐาน (Process Standards Legend)
        st.markdown("""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px 18px; font-size: 13px; color: #CCCCCC; margin-top: 10px;">
                <b style="color: #F0B90B;">📌 เกณฑ์มาตรฐานอ้างอิง (Process Standards):</b><br>
                • <b>Dryer:</b> Max Temp <b>175 - 260 °C</b> | Dwell Time >175°C <b>> 1:00 min (>60s)</b><br>
                • <b>Debinder:</b> Max Temp <b>200 - 375 °C</b> | Dwell Time >175°C <b>> 2:00 min (>120s)</b><br>
                • <b>Brazing Max Temp:</b> Corner Probes <b>596 - 610 °C</b> | Center Probes (#2, #5) <b>583 - 607 °C</b><br>
                • <b>Brazing Dwell Time >577°C:</b> <b>2:30 - 6:00 min (150s - 360s)</b><br>
                • <b>Brazing Dwell Time >583°C:</b> <b>2:30 - 6:00 min (150s - 360s)</b><br>
                • <b>Brazing Dwell Time >600°C:</b> <b>< 4:00 min (<240s)</b>
            </div>
        """, unsafe_allow_html=True)

        # ส่วนตรวจสอบและเลือกดาวน์โหลด Excel (.xlsx)
        with st.expander("📋 ตรวจสอบและเลือกดาวน์โหลดตารางข้อมูล Excel (.xlsx)"):
            st.dataframe(df)
            
            st.markdown("---")
            st.markdown("##### 📥 ตัวเลือกการดาวน์โหลดไฟล์ Excel")
            
            col_opt1, col_opt2 = st.columns([2, 1])
            with col_opt1:
                custom_filename = st.text_input(
                    "ตั้งชื่อไฟล์ดาวน์โหลด:", 
                    value="datapaq_nb1_8probes_data.xlsx"
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
