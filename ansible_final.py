import subprocess
import os # <--- STEP 1: Import the 'os' library

# ฟังก์ชันนี้ต้องรับ student_id และ router_name มาจากไฟล์หลัก
# เพื่อสร้างชื่อไฟล์และส่งเป็นตัวแปรให้ playbook
def showrun(student_id, router_name):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess

    # สร้างชื่อไฟล์ที่เราคาดหวังว่าจะได้จาก playbook
    filename = f"show_run_{student_id}_{router_name}.txt"
    
    # ประกอบร่างคำสั่ง ansible-playbook ให้สมบูรณ์
    # -i hosts: ระบุ inventory file
    # --extra-vars: ส่งตัวแปรจาก Python เข้าไปใน playbook
    command = [
        'ansible-playbook',
        'playbook.yaml',
        '-i', 'hosts',
        '--extra-vars', f"student_id={student_id} router_name={router_name}"
    ]

    # --- THE FINAL FIX IS HERE ---
    # STEP 2: Explicitly tell Ansible where to find its configuration file.
    # This forces it to read 'host_key_checking = False'
    env = os.environ.copy()
    env['ANSIBLE_CONFIG'] = './ansible.cfg'
    # ---------------------------

    # รันคำสั่ง, but now with the correct environment
    result = subprocess.run(command, capture_output=True, text=True, env=env) # <--- STEP 3: Add env=env
    
    # เก็บผลลัพธ์ stdout เพื่อนำมาตรวจสอบ
    ansible_output = result.stdout
    print("----- Ansible Output -----")
    print(ansible_output)
    print("--------------------------")

    # ตรวจสอบผลลัพธ์: 'ok=2' หมายถึง 2 tasks สำเร็จ และ 'failed=0' คือไม่มี task ไหนล้มเหลว
    if 'ok=2' in ansible_output and 'failed=0' in ansible_output:
        # ถ้าสำเร็จ คืนค่า 'ok' และชื่อไฟล์ที่สร้างขึ้น
        return "ok", filename
    else:
        # ถ้าล้มเหลว คืนค่า Error และ None สำหรับชื่อไฟล์
        return "Error: Ansible", None