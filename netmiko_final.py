from netmiko import ConnectHandler
import re # <-- (เพิ่ม) import สำหรับ get_motd

# -----------------------------------------------------------------
# (1) ฟังก์ชัน GIGABIT_STATUS (วิธีเดิม)
# -----------------------------------------------------------------
# (สมมติว่าคุณมีฟังก์ชัน gigabit_status อยู่แล้ว)
# def gigabit_status():
#    ... (โค้ด gigabit_status ของคุณ) ...
#    return "GigabitEthernet1 is up/up"


# -----------------------------------------------------------------
# (2) ฟังก์ชัน GET_MOTD (วิธีใหม่ที่ใช้ re.DOTALL)
# -----------------------------------------------------------------
def get_motd(host_ip):
    """
    ใช้ Netmiko (show run) และ Regex (DOTALL) เพื่อดึง MOTD
    """

    # (!!!) -----------------------------------------------------------------
    # (!!!) **สำคัญ:** แก้ไข USERNAME/PASSWORD ให้ถูกต้อง
    # (!!!) (ต้องตรงกับที่ใช้ใน Netconf/Restconf/Ansible)
    # (!!!) -----------------------------------------------------------------
    device_params = {
        'device_type': 'cisco_ios',
        'host': host_ip,
        'username': 'admin',
        'password': 'cisco',
    }

    try:
        with ConnectHandler(**device_params) as connection:
            # ดึง 'show run' ทั้งหมด (ตามโค้ดตัวอย่างของคุณ)
            running_config = connection.send_command("show running-config", use_textfsm=False)

            # ใช้ re.DOTALL เพื่อให้ '.' จับคู่ newline ได้ (กรณี MOTD หลายบรรทัด)
            match = re.search(r"banner motd (.)(.*?)\1", running_config, re.DOTALL)

            if match:
                # Group 2 คือข้อความ MOTD
                motd_message = match.group(2).strip()

                # ตรวจสอบว่าข้อความว่างเปล่าหรือไม่ (เช่น banner motd ##)
                if motd_message:
                    return motd_message
                else:
                    return "Error: No MOTD Configured"
            else:
                # ถ้าไม่เจอ 'banner motd ...' เลย
                return "Error: No MOTD Configured"

    except Exception as e:
        print(f"Error connecting or reading MOTD: {e}")
        return f"Error: Could not connect to {host_ip} or read MOTD"