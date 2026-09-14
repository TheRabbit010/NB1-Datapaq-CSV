# คำนวณช่วง Tick สำหรับแกน Time ให้เหมาะสม (แสดงประมาณ 15-20 ค่า)
        step_tick = max(1, len(df) // 16)
        tick_indices = list(range(0, len(df), step_tick))
        if (len(df) - 1) not in tick_indices:
            tick_indices.append(len(df) - 1)
            
        # สร้างรายการ Tick สำหรับแกน Distance โดยเฉพาะ เพื่อให้สเกลดูดีแบบทีละ 2.00 หรือ 4.00
        max_dist = df["Distance (m)"].max()
        if max_dist <= 20:
            dist_dtick = 1.0
        elif max_dist <= 50:
            dist_dtick = 2.0
        else:
            dist_dtick = 4.0

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
            yaxis=dict(
                title=dict(text="Temperature (°C)", font=dict(color="#FFFFFF", size=12)),
                tickfont=dict(color="#CCCCCC", size=10),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.08)",
                zeroline=False,
                linecolor="#555555",
                domain=[0.22, 1.0],
                range=[0, 650]
            ),
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
                position=0.12,
                tickangle=0 # ให้ตัวเลขเวลาแสดงเป็นแนวนอน
            ),
            xaxis2=dict(
                title=dict(text="Distance (m)", font=dict(color="#F0B90B", size=11)),
                overlaying="x",
                anchor="free",
                position=0.00,
                
                # ปรับแต่งสเกล Distance ใหม่ให้เป็นเชิงเส้น (Linear) และกำหนดระยะห่างของขีด
                tickmode="linear",
                tick0=0,
                dtick=dist_dtick,
                tickformat=".2f", # บังคับทศนิยม 2 ตำแหน่ง
                
                # กำหนดให้ Range ของแกน Distance แมปตรงกับแกน X หลัก
                range=[0, max_dist],
                
                tickfont=dict(color="#F0B90B", size=10),
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor="#F0B90B",
                
                # ---------------------------------------------------------
                # เพิ่มขีดย่อย (Minor Ticks) และจัดตัวอักษรให้อยู่ในแนวนอน
                # ---------------------------------------------------------
                minor=dict(
                    tickmode="linear",
                    tick0=0,
                    dtick=dist_dtick / 2, # ขีดย่อยจะถี่กว่าขีดหลัก 2 เท่า
                    ticklen=4,
                    tickcolor="#F0B90B",
                    showgrid=False
                ),
                tickangle=0, # บังคับตัวเลขให้อยู่ในแนวนอน (0 องศา)
                ticks="outside",
                ticklen=6, # ความยาวขีดหลัก
            ),
            height=660,
            margin=dict(l=60, r=240, t=50, b=120)
        )
