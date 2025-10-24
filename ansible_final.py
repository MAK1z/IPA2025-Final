import ansible_runner
import os
import shutil
import time
import subprocess # <-- (เพิ่ม) import สำหรับ set_motd
import json
import base64

# -----------------------------------------------------------------
# (1) ฟังก์ชัน SHOWRUN (วิธีเดิมที่ใช้ ansible-runner)
# -----------------------------------------------------------------
# (สมมติว่าคุณมีฟังก์ชัน showrun อยู่แล้ว)
# def showrun(student_id, router_name):
#    ... (โค้ด showrun ที่ใช้ ansible-runner ของคุณ) ...
#    return "ok", "filename.txt"


# -----------------------------------------------------------------
# (2) ฟังก์ชัน SET_MOTD (วิธีใหม่ที่ใช้ subprocess)
# -----------------------------------------------------------------
def set_motd(host_ip, message):
    """
    ใช้ ansible-playbook (subprocess) เพื่อตั้งค่า MOTD (เข้ารหัส Base64)
    """
    playbook_path = 'motd_playbook.yaml'
    inventory_path = 'hosts'

    ansible_executable = shutil.which('ansible-playbook')

    if not ansible_executable:
        print("Error: 'ansible-playbook' command not found.")
        return "Error: 'ansible-playbook' command not found."


    # (V--- [นี่คือการแก้ไข] ---V)
    # 1. เข้ารหัสข้อความ (Message) เป็น Base64
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')

    # 2. สร้าง Dictionary (ใช้ชื่อตัวแปรใหม่)
    vars_dict = {
        "motd_message_b64": base64_message
    }
    # 3. แปลง Dictionary เป็น JSON String (ปลอดภัยที่สุด)
    extra_vars = json.dumps(vars_dict)
    # (A--- [จบการแก้ไข] ---A)


    # สร้างคำสั่งที่จะรัน
    command_args = [
        ansible_executable,
        "-i", inventory_path,
        playbook_path,
        "--limit", host_ip,
        "-e", extra_vars # <-- ใช้ตัวแปร JSON ที่แก้ไขแล้ว
    ]

    try:
        print(f"Running command: {' '.join(command_args)}")
        # รันคำสั่ง
        process = subprocess.run(command_args, capture_output=True, text=True, check=True, timeout=90)

        # ตรวจสอบผลลัพธ์ว่าสำเร็จ (failed=0 และ changed=1)
        if 'failed=0' in process.stdout and 'changed=1' in process.stdout:
            print("Ansible MOTD command successful (changed=1).")
            return "Ok: success"
        elif 'failed=0' in process.stdout:
             print("Ansible MOTD command successful (changed=0).")
             return "Ok: success (No changes needed)"
        else:
            print(f"Ansible MOTD command failed. Output:\n{process.stdout}\n{process.stderr}")
            return "Error: Failed to set MOTD via Ansible."

    except subprocess.CalledProcessError as e:
        print(f"Ansible execution failed:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        return f"Error: Ansible execution failed. Check logs."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"