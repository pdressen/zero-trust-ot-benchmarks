from pyModbusTCP.client import ModbusClient
from time import sleep, perf_counter
from json import load
from statistics import stdev

# consts
NUM_ITERATIONS = 1_000   # how many times to run a read/write cycle

# load config.json
config = None
with open("config.json", "r") as config_file:
    config = load(config_file)

# create ModbusTCP client (master)
c = ModbusClient(host=config["modbus_tcp"]["host"], port=config["modbus_tcp"]["port"], unit_id=config["modbus_tcp"]["id"], auto_open=True)
if c.open():
    # let everything settle for a moment
    print("Connection successful")
    print("Waiting for things to settle (sleep)...")
    sleep(5)

    # benchmark reading & writing
    print(f"Performing {NUM_ITERATIONS} read-write cycles...")
    durations = arr = [0 for i in range(NUM_ITERATIONS)]     
    for i in range(0, NUM_ITERATIONS):
        start_time = perf_counter()

        # read
        regs = c.read_holding_registers(0, 100)        
        if not regs:
            raise Exception(c.last_error_as_txt)
        
        # write
        # if not c.write_multiple_registers(30000, regs):
        #     raise Exception(c.last_error_as_txt)
        
        duration = perf_counter() - start_time
        durations[i] = duration

    
    print(f"Done")
    print("#total\tmax\tmin\tavg\tstddev")
    print(f"{sum(durations):.4f}\t{max(durations):.4f}\t{min(durations):.4f}\t{(sum(durations)/len(durations)):.4f}\t{stdev(durations):.4f}")
        
else:
    print(f"Error opening modbus connection: {c.last_error_as_txt}")
