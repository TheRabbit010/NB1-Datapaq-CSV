if color_shading_mode == "แสดงสีตามโซน (By Zone)":
            zones_data = [
                # โทนอุ่น (Dryer) -> อุณหภูมิเริ่มสูงขึ้น
                {"Start Time": "00:00:00", "End Time": "00:02:14", "Zone Name": "Dryer Z#1", "Color": "#F7DC6F"}, # เหลืองอ่อน
                {"Start Time": "00:02:15", "End Time": "00:04:28", "Zone Name": "Dryer Z#2", "Color": "#F39C12"}, # ส้มเหลือง
                {"Start Time": "00:04:29", "End Time": "00:04:58", "Zone Name": "EXT Dryer", "Color": "#E67E22"}, # ส้ม
                
                # โทนร้อน (Debinder) -> ร้อนขึ้นเรื่อยๆ
                {"Start Time": "00:04:59", "End Time": "00:05:26", "Zone Name": "ENT DB", "Color": "#D35400"},    # ส้มเข้ม
                {"Start Time": "00:05:27", "End Time": "00:07:41", "Zone Name": "DB Z#1", "Color": "#E74C3C"},    # แดงส้มสว่าง
                {"Start Time": "00:07:42", "End Time": "00:09:32", "Zone Name": "DB Z#2", "Color": "#E63946"},    # แดงปานกลาง
                {"Start Time": "00:09:33", "End Time": "00:11:23", "Zone Name": "DB Z#3", "Color": "#D90429"},    # แดงสด
                {"Start Time": "00:11:24", "End Time": "00:13:38", "Zone Name": "DB Z#4", "Color": "#C1121F"},    # แดงเข้ม
                
                # โซนเชื่อมต่อ
                {"Start Time": "00:13:39", "End Time": "00:15:34", "Zone Name": "XFER#1", "Color": "#9B59B6"},    # ม่วง (เชื่อมต่อความร้อน)
                
                # โทนร้อนจัด (Brazing) -> ร้อนที่สุด (Peak) สีแดงเพลิง
                {"Start Time": "00:15:35", "End Time": "00:17:48", "Zone Name": "Z#1", "Color": "#FF0033"},       
                {"Start Time": "00:17:49", "End Time": "00:19:43", "Zone Name": "Z#2", "Color": "#E6002E"},       
                {"Start Time": "00:19:44", "End Time": "00:21:40", "Zone Name": "Z#3", "Color": "#CC0029"},       
                {"Start Time": "00:21:41", "End Time": "00:23:07", "Zone Name": "Z#4", "Color": "#B30024"},       # Peak แดงเข้มจัด
                {"Start Time": "00:23:08", "End Time": "00:24:33", "Zone Name": "Z#5", "Color": "#CC0029"},       
                {"Start Time": "00:24:34", "End Time": "00:25:59", "Zone Name": "Z#6", "Color": "#E6002E"},       
                {"Start Time": "00:26:00", "End Time": "00:27:37", "Zone Name": "Z#7", "Color": "#FF0033"},       
                
                # โทนเย็น (Cooling) -> ลดอุณหภูมิกะทันหัน
                {"Start Time": "00:27:38", "End Time": "00:29:19", "Zone Name": "WatCool#1", "Color": "#00B4D8"}, # ฟ้าสดใส
                {"Start Time": "00:29:20", "End Time": "00:30:41", "Zone Name": "WatCool#2", "Color": "#0096C7"}, # ฟ้าอมน้ำเงิน
                {"Start Time": "00:30:42", "End Time": "00:32:02", "Zone Name": "Exit curtain box", "Color": "#0077B6"}, # น้ำเงิน
                {"Start Time": "00:32:03", "End Time": "00:32:28", "Zone Name": "XFER#2", "Color": "#023E8A"},    # น้ำเงินเข้ม
                {"Start Time": "00:32:29", "End Time": "00:33:21", "Zone Name": "AirCool#1", "Color": "#48CAE4"}, # ฟ้าลมเย็น
                {"Start Time": "00:33:22", "End Time": "00:34:15", "Zone Name": "AirCool#2", "Color": "#90E0EF"}, # ฟ้าสว่าง
                {"Start Time": "00:34:16", "End Time": "00:35:35", "Zone Name": "Exit", "Color": "#CAF0F8"}       # ขาวอมฟ้า (อุณหภูมิห้อง)
            ]
            angle_setting = -90
        else:
            # กรณีเลือกโหมดแสดงสีตามกลุ่มงาน (Process Group)
            zones_data = [
                {"Start Time": "00:00:00", "End Time": "00:04:58", "Zone Name": "Dryer", "Color": "#F39C12"},      # ส้ม
                {"Start Time": "00:04:59", "End Time": "00:15:34", "Zone Name": "Debinder", "Color": "#E74C3C"},   # แดงส้ม
                {"Start Time": "00:15:35", "End Time": "00:27:37", "Zone Name": "Brazing", "Color": "#FF0033"},    # แดงเพลิง
                {"Start Time": "00:27:38", "End Time": "00:34:15", "Zone Name": "Cool", "Color": "#00B4D8"},       # ฟ้าเย็น
                {"Start Time": "00:34:16", "End Time": "00:35:35", "Zone Name": "Exit", "Color": "#90E0EF"}        # ฟ้าสว่าง
            ]
            angle_setting = 0
