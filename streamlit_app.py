# ---------------------------------------------------------
        # 📊 ตารางสรุปค่า (จัดกลุ่มหัวคอลัมน์แยกตามกลุ่มงาน)
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

        # จัดลำดับ Probe (PB#1, PB#2, PB#3, PB#8 = Bottom / PB#4, PB#5, PB#6, PB#7 = Top)
        probe_order = [1, 2, 3, 8, 4, 5, 6, 7]
        ordered_cols = []
        for p_num in probe_order:
            for c in probe_cols[:8]:
                if f"Probe #{p_num}" in c:
                    ordered_cols.append((p_num, c))
                    break

        summary_rows = []
        for p_num, col_name in ordered_cols:
            location = "Bottom" if p_num in [1, 2, 3, 8] else "Top"
            short_pb_name = f"PB#{p_num}"
            
            # 1. Maximum Temperatures (°C)
            d_max = round(dryer_subset[col_name].max(), 1) if not dryer_subset.empty else 0.0
            db_max = round(debinder_subset[col_name].max(), 1) if not debinder_subset.empty else 0.0
            br_max = round(brazing_subset[col_name].max(), 1) if not brazing_subset.empty else 0.0
            
            # 2. Dwell Times
            br_dwell_600 = (brazing_subset[col_name] > 600).sum() if not brazing_subset.empty else 0
            br_dwell_583 = (brazing_subset[col_name] > 583).sum() if not brazing_subset.empty else 0
            br_dwell_577 = (brazing_subset[col_name] > 577).sum() if not brazing_subset.empty else 0
            
            db_dwell_200 = (debinder_subset[col_name] > 200).sum() if not debinder_subset.empty else 0
            d_dwell_175 = (dryer_subset[col_name] > 175).sum() if not dryer_subset.empty else 0

            summary_rows.append([
                location,
                short_pb_name,
                br_max,
                db_max,
                d_max,
                format_excel_time(br_dwell_600),
                format_excel_time(br_dwell_583),
                format_excel_time(br_dwell_577),
                format_excel_time(db_dwell_200),
                format_excel_time(d_dwell_175)
            ])

        # กำหนดหัวตาราง 2 ชั้น (MultiIndex Header) เพื่อระบุกลุ่มงานของ Dwell Time
        multi_cols = pd.MultiIndex.from_tuples([
            ("", "Location"),
            ("", "Probe"),
            ("Max Temp (°C)", "Brazing"),
            ("Max Temp (°C)", "Debinder"),
            ("Max Temp (°C)", "Dryer"),
            ("Dwell Time [Brazing Zone]", "at 600°C / probe"),
            ("Dwell Time [Brazing Zone]", "at 583°C / probe"),
            ("Dwell Time [Brazing Zone]", "at 577°C / probe"),
            ("Dwell Time [Debinder Zone]", "at 200°C / probe"),
            ("Dwell Time [Dryer Zone]", "at 175°C / probe")
        ])

        display_summary_df = pd.DataFrame(summary_rows, columns=multi_cols)

        st.dataframe(display_summary_df, use_container_width=True)
