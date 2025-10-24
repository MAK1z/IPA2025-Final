#######################################################################################
# Yourname: Natakorn Hormpanna
# Your student ID: 66070055
# Your GitHub Repo: https://github.com/MAK1z/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
import os
import requests
import json
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder

# เลือก import แค่ตัวเดียวระหว่าง restconf_final หรือ netconf_final
import restconf_final 
import netconf_final # <-- **การเปลี่ยนแปลงที่ 1: เพิ่ม netconf_final**

import netmiko_final
import ansible_final

#######################################################################################
# 2. Assign the Webex access token and Room ID to variables using environment variables.

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")
ROOM_ID = os.environ.get("WEBEX_ROOM_ID") 

# Check if environment variables are set
if not ACCESS_TOKEN or not ROOM_ID:
    raise Exception("\n!!! Environment variables not set. !!!\n"
                    "Please set WEBEX_ACCESS_TOKEN and WEBEX_ROOM_ID before running the script.\n"
                    "Example:\n"
                    "export WEBEX_ACCESS_TOKEN='Your_Token_Here'\n"
                    "export WEBEX_ROOM_ID='Your_Room_ID_Here'")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# <-- **การเปลี่ยนแปลงที่ 2: เพิ่มตัวแปรสำหรับเก็บ state และ IP ที่อนุญาต**
selected_method = None # เก็บ 'restconf' หรือ 'netconf'
VALID_IPS = ["10.0.15.61", "10.0.15.62", "10.0.15.63", "10.0.15.64", "10.0.15.65"]
COMMANDS_NEED_IP = ["create", "delete", "enable", "disable", "status"]


while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #   "roomId" is the ID of the selected room
    #   "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": ROOM_ID, "max": 1} 

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    my_student_id = "66070055"
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #   e.g.  "/66070055 10.0.15.61 create"
    parts = message.split()
    if message.startswith(f"/{my_student_id}") and len(parts) > 1:

        args = parts[1:] # รายการ arguments หลัง student ID
        command = args[0] # คำสั่งแรก (อาจเป็น IP, 'restconf', 'showrun', 'create' ฯลฯ)
        print(f"Parsed arguments: {args}")

# 5. Complete the logic for each command
        
        # Initialize filename to None for other commands
        filename = None 
        responseMessage = None # ตั้งค่าเริ่มต้นเป็น None

        # <-- **การเปลี่ยนแปลงที่ 3: ปรับปรุง Logic ทั้งหมด**

        if command == "restconf":
            selected_method = "restconf"
            responseMessage = "Ok: Restconf"
        
        elif command == "netconf":
            selected_method = "netconf"
            responseMessage = "Ok: Netconf"

        elif command == "gigabit_status":
            responseMessage = netmiko_final.gigabit_status()
        
        elif command == "showrun":
            router_name = 'CSR1KV-Pod1-1'
            responseMessage, filename = ansible_final.showrun(my_student_id, router_name)

        elif command in VALID_IPS:
            ip_address = command
            if len(args) < 2:
                responseMessage = "Error: No command found."
            else:
                actual_command = args[1]
                if actual_command not in COMMANDS_NEED_IP:
                     responseMessage = "Error: No command or unknown command"
                elif selected_method is None:
                    responseMessage = "Error: No method specified"
                
                elif selected_method == "restconf":
                    if actual_command == "create":
                        responseMessage = restconf_final.create(my_student_id, ip_address)
                    elif actual_command == "delete":
                        responseMessage = restconf_final.delete(my_student_id, ip_address)
                    elif actual_command == "enable":
                        responseMessage = restconf_final.enable(my_student_id, ip_address)
                    elif actual_command == "disable":
                        responseMessage = restconf_final.disable(my_student_id, ip_address)
                    elif actual_command == "status":
                        responseMessage = restconf_final.status(my_student_id, ip_address)
                
                elif selected_method == "netconf":
                    if actual_command == "create":
                        responseMessage = netconf_final.create(my_student_id, ip_address)
                    elif actual_command == "delete":
                        responseMessage = netconf_final.delete(my_student_id, ip_address)
                    elif actual_command == "enable":
                        responseMessage = netconf_final.enable(my_student_id, ip_address)
                    elif actual_command == "disable":
                        responseMessage = netconf_final.disable(my_student_id, ip_address)
                    elif actual_command == "status":
                        responseMessage = netconf_final.status(my_student_id, ip_address)

        elif command in COMMANDS_NEED_IP:
            if selected_method is None:
                responseMessage = "Error: No method specified"
            else:
                responseMessage = "Error: No IP specified"
        
        else:
            responseMessage = "Error: No command or unknown command"


# 6. Complete the code to post the message to the Webex Teams room.
        
        # ตรวจสอบว่ามี responseMessage ที่ต้องส่งหรือไม่ (ป้องกันการส่งค่า None)
        if responseMessage:
            if command == "showrun" and responseMessage == 'ok':
                fileobject = open(filename, 'rb')
                filetype = "text/plain"
                
                payload = {
                    "roomId": ROOM_ID, # <-- **การเปลี่ยนแปลงที่ 3 (จากโค้ดเดิม)**
                    "text": "show running config",
                    "files": (filename, fileobject, filetype),
                }
                postData = MultipartEncoder(fields=payload)
                
                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": postData.content_type,
                }
            else:
                payload = {"roomId": ROOM_ID, "text": responseMessage} # <-- **การเปลี่ยนแปลงที่ 4 (จากโค้ดเดิม)**
                postData = json.dumps(payload)

                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}", 
                    "Content-Type": "application/json"
                }   

            # Post the call to the Webex Teams message API.
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=postData,
                headers=HTTPHeaders,
            )
            if not r.status_code == 200:
                raise Exception(
                    "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text)
                )