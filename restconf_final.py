import json
import requests
requests.packages.urllib3.disable_warnings()

# (ลบ ROUTER_IP และ api_url_base ที่ hard-code ไว้ออก)

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 1**
    # **การเปลี่ยนแปลงที่ 2: สร้าง URL โดยใช้ ip_address ที่รับมา**
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    # คำนวณ IP Address จาก 3 ตัวท้ายของรหัสนักศึกษา
    last_three_digits = student_id[-3:]
    x = int(last_three_digits[0])
    y = int(last_three_digits[1:])
    # (เปลี่ยนชื่อตัวแปร ip_address เป็น loopback_ip เพื่อไม่ให้ซ้ำกับพารามิเตอร์)
    loopback_ip = f"172.{x}.{y}.1" 

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": loopback_ip, # <-- ใช้ IP ที่คำนวณ
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }

    resp = requests.put(
        url=api_url, # <-- **การเปลี่ยนแปลงที่ 2**
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        # **การเปลี่ยนแปลงที่ 3: ปรับปรุงข้อความ return**
        return f"Interface loopback {student_id} is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        if resp.status_code == 409: # Conflict
            return f"Cannot create: Interface loopback {student_id}"
        return f"Error: Cannot create interface loopback {student_id}"


def delete(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 1**
    # **การเปลี่ยนแปลงที่ 2**
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    resp = requests.delete(
        url=api_url, # <-- **การเปลี่ยนแปลงที่ 2**
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
         # **การเปลี่ยนแปลงที่ 3**
        return f"Interface loopback {student_id} is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        if resp.status_code == 404: # Not Found
            return f"Cannot delete: Interface loopback {student_id}"
        return f"Error: Cannot delete interface loopback {student_id}"


def enable(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 1**
    # **การเปลี่ยนแปลงที่ 2**
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"
    
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "enabled": True
        }
    }

    resp = requests.patch( # ใช้ PATCH สำหรับการแก้ไขบางส่วน
        url=api_url, # <-- **การเปลี่ยนแปลงที่ 2**
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
         # **การเปลี่ยนแปลงที่ 3**
        return f"Interface loopback {student_id} is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        if resp.status_code == 404:
            return f"Cannot enable: Interface loopback {student_id}"
        return f"Error: Cannot enable interface loopback {student_id}"


def disable(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 1**
    # **การเปลี่ยนแปลงที่ 2**
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "enabled": False
        }
    }

    resp = requests.patch( # ใช้ PATCH สำหรับการแก้ไขบางส่วน
        url=api_url, # <-- **การเปลี่ยนแปลงที่ 2**
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
         # **การเปลี่ยนแปลงที่ 3**
        return f"Interface loopback {student_id} is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        if resp.status_code == 404:
             # **การเปลี่ยนแปลงที่ 3**
            return f"Cannot shutdown: Interface loopback {student_id} (checked by Restconf)"
        return f"Error: Cannot shutdown interface loopback {student_id} (checked by Restconf)"


def status(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 1**
    # **การเปลี่ยนแปลงที่ 2**
    api_url_status = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{student_id}"

    resp = requests.get(
        url=api_url_status, # <-- **การเปลี่ยนแปลงที่ 2**
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        
        # ตรวจสอบว่า key "admin-status" มีอยู่จริงหรือไม่
        if "ietf-interfaces:interface" in response_json and "admin-status" in response_json["ietf-interfaces:interface"]:
            admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
            oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
            
            if admin_status == 'up' and oper_status == 'up':
                 # **การเปลี่ยนแปลงที่ 3**
                return f"Interface loopback {student_id} is enabled (checked by Restconf)"
            elif admin_status == 'down' and oper_status == 'down':
                 # **การเปลี่ยนแปลงที่ 3**
                return f"Interface loopback {student_id} is disabled (checked by Restconf)"
            else:
                return f"Interface loopback {student_id} state is {admin_status}/{oper_status} (checked by Restconf)"
        else:
            return f"Could not parse status for interface loopback {student_id} (checked by Restconf)"

    # <-- **การเปลี่ยนแปลงที่ 4 (แก้ไข Bug)**: ย้าย elif ออกมานอก if block แรก
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
         # **การเปลี่ยนแปลงที่ 3**
        return f"No Interface loopback {student_id} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
         # **การเปลี่ยนแปลงที่ 3**
        return f"Error: Cannot get status for interface loopback {student_id} (checked by Restconf)"