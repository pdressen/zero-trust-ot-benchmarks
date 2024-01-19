from pyModbusTCP.client import ModbusClient
from time import sleep
from json import load

# load config.json
config = None
with open("config.json", "r") as config_file:
    config = load(config_file)

# create ModbusTCP client (master)
c = ModbusClient(host=config["modbus_tcp"]["host"], port=config["modbus_tcp"]["port"], unit_id=config["modbus_tcp"]["id"], auto_open=True)
if c.open():

    # continuously read the holding registers
    while c.is_open:
        regs = c.read_holding_registers(0, 100)

        if regs:
            print(regs)
        else:
            print("read error")

        sleep(1)
else:
    print(f"Error opening modbus connection: {c.last_error_as_txt}")
