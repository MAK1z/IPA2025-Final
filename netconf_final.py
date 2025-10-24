from ncclient import manager
import xmltodict
from ncclient.operations.rpc import RPCError

# (ลบ ROUTER_IP และ m ที่เชื่อมต่อแบบ global ออก)

# **การเปลี่ยนแปลงที่ 1: สร้างฟังก์ชัน helper สำหรับเชื่อมต่อ**
def get_manager(ip_address):
    """
    เชื่อมต่อ NETCONF manager ไปยัง IP ที่ระบุ
    """
    return manager.connect(
        host=ip_address,
        port=830, # Standard NETCONF port
        username="admin",
        password="cisco",
        hostkey_verify=False
    )

def create(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 2**
    # คำนวณ IP Address จาก 3 ตัวท้ายของรหัสนักศึกษา
    last_three_digits = student_id[-3:]
    x = int(last_three_digits[0])
    y = int(last_three_digits[1:])
    loopback_ip = f"172.{x}.{y}.1" # (เปลี่ยนชื่อตัวแปรไม่ให้ซ้ำ)

    # XML Payload สำหรับสร้าง Interface
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{loopback_ip}</ip>
              <netmask>255.255.255.0</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """

    try:
        # **การเปลี่ยนแปลงที่ 3: ส่ง ip_address ไปยัง status**
        current_status = status(student_id, ip_address)
        if "No Interface" not in current_status:
             # (ข้อความนี้ตรงกับตัวอย่างของคุณ)
            return f"Cannot create: Interface loopback {student_id}"

        # **การเปลี่ยนแปลงที่ 4: ใช้ 'with' และ 'get_manager'**
        with get_manager(ip_address) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                # **การเปลี่ยนแปลงที่ 5: ปรับปรุงข้อความ return**
                return f"Interface loopback {student_id} is created successfully using Netconf"
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Error: Cannot create interface loopback {student_id}"
    # **(ลบฟังก์ชัน netconf_edit_config ที่ไม่จำเป็นออก)**


def delete(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 2**
    # XML Payload สำหรับลบ Interface (ใช้ operation="delete")
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>Loopback{student_id}</name>
        </interface>
      </interfaces>
    </config>
    """

    try:
        # **การเปลี่ยนแปลงที่ 3**
        if "No Interface" in status(student_id, ip_address):
            return f"Cannot delete: Interface loopback {student_id}"

        # **การเปลี่ยนแปลงที่ 4**
        with get_manager(ip_address) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                # **การเปลี่ยนแปลงที่ 5**
                return f"Interface loopback {student_id} is deleted successfully using Netconf"
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Error: Cannot delete interface loopback {student_id}"


def enable(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 2**
    # XML Payload สำหรับแก้ไขค่า 'enabled' เป็น 'true'
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
         # **การเปลี่ยนแปลงที่ 3**
        if "No Interface" in status(student_id, ip_address):
            return f"Cannot enable: Interface loopback {student_id}"

        # **การเปลี่ยนแปลงที่ 4**
        with get_manager(ip_address) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                 # **การเปลี่ยนแปลงที่ 5**
                return f"Interface loopback {student_id} is enabled successfully using Netconf"
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Error: Cannot enable interface loopback {student_id}"


def disable(student_id, ip_address): # <-- **การเปลี่ยนแปลงที่ 2**
    # XML Payload สำหรับแก้ไขค่า 'enabled' เป็น 'false'
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{student_id}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
         # **การเปลี่ยนแปลงที่ 3**
        if "No Interface" in status(student_id, ip_address):
             # **การเปลี่ยนแปลงที่ 5**
            return f"Cannot shutdown: Interface loopback {student_id} (checked by Netconf)"

        # **การเปลี่ยนแปลงที่ 4**
        with get_manager(ip_address) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                 # **การเปลี่ยนแปลงที่ 5**
                return f"Interface loopback {student_id} is shutdowned successfully using Netconf"
    except RPCError as e:
        print(f"Error: {e.message}")
         # **การเปลี่ยนแปลงที่ 5**
        return f"Error: Cannot shutdown interface loopback {student_id} (checked by Netconf)"


def status(student_id, ip_address): # <-- **(แก้ไข Bug NoneType)**
    # XML Filter เพื่อขอข้อมูลเฉพาะ interface ที่ต้องการ
    netconf_filter = f"""
    <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      <interface>
        <name>Loopback{student_id}</name>
      </interface>
    </interfaces-state>
    """

    try:
        with get_manager(ip_address) as m:
            netconf_reply = m.get(filter=('subtree', netconf_filter))

        print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # (V-- FIX --V)
        # ดึง <data> ออกมาก่อน
        rpc_data = netconf_reply_dict.get('rpc-reply', {}).get('data')

        # ตรวจสอบว่า rpc_data เป็น None (กรณี <data></data>) หรือไม่
        if rpc_data is None:
            interface_data = None
        else:
            # ถ้า rpc_data ไม่ใช่ None ค่อย .get() ต่อ
            interface_data = rpc_data.get('interfaces-state', {}).get('interface')
        # (^-- END OF FIX --^)


        if interface_data: # ถ้า interface_data ไม่ใช่ None (คือมีข้อมูล)
            admin_status = interface_data.get('admin-status')
            oper_status = interface_data.get('oper-status')
            if admin_status == 'up' and oper_status == 'up':
                return f"Interface loopback {student_id} is enabled (checked by Netconf)"
            elif admin_status == 'down' and oper_status == 'down':
                return f"Interface loopback {student_id} is disabled (checked by Netconf)"
            else:
                return f"Interface loopback {student_id} state is {admin_status}/{oper_status} (checked by Netconf)"

        else: # ถ้า interface_data เป็น None (เพราะ rpc_data เป็น None หรือหา 'interface' ไม่เจอ)
            return f"No Interface loopback {student_id} (checked by Netconf)"

    except RPCError as e:
       print(f"Error: {e.message}")
       return f"Error: Cannot get status for interface loopback {student_id} (checked by Netconf)"