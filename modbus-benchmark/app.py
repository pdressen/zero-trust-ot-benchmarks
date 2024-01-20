from pyModbusTCP.client import ModbusClient
from time import sleep, perf_counter
from json import load
from statistics import stdev

# consts
NUM_REGS = 96
NUM_ITERATIONS = 1_000   # how many times to run a read/write cycle
OUTPUT_VERBOSE_TIMING = True    # if each single cycle time should be logged

# load config.json
config = None
with open("config.json", "r") as config_file:
    config = load(config_file)
MODBUS_TCP_HOST = config["modbus_tcp"]["host"]
MODBUS_TCP_PORT = config["modbus_tcp"]["port"]
MODBUS_TCP_ID = config["modbus_tcp"]["id"]

# create ModbusTCP client (master)
print(f"Connecting to {MODBUS_TCP_HOST}:{MODBUS_TCP_PORT}, unit-ID {MODBUS_TCP_ID}...")
c = ModbusClient(host=MODBUS_TCP_HOST, port=config["modbus_tcp"]["port"], unit_id=config["modbus_tcp"]["id"], auto_open=True)
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
        hregs = c.read_holding_registers(0, NUM_REGS)        
        if not hregs:
            raise Exception(c.last_error_as_txt)
        coils = c.read_coils(0, NUM_REGS)        
        if not coils:
            raise Exception(c.last_error_as_txt)
        
        # write
        if not c.write_multiple_registers(0, hregs):
             raise Exception(c.last_error_as_txt)        
        if not c.write_multiple_coils(0, coils):
             raise Exception(c.last_error_as_txt)
        
        duration = perf_counter() - start_time
        durations[i] = duration

    
    c.close()

    print(f"Done")
    
    if OUTPUT_VERBOSE_TIMING:
        print("######## INDIVIDUAL CYCLE DURATIONS #########")
        print("#cycle\tduration")
        for i in range(len(durations)):
            print(f"{i}\t{durations[i]:.4f}")

    print("######## SUMMARY #########")
    print("#total\tmax\tmin\tavg\tstddev")
    std_deviation = stdev(durations) if (len(durations) > 1)  else 0
    print(f"{sum(durations):.4f}\t{max(durations):.4f}\t{min(durations):.4f}\t{(sum(durations)/len(durations)):.4f}\t{std_deviation:.4f}")

    print("#################")
    print("Note: All times in seconds")
        
else:
    print(f"Error opening modbus connection: {c.last_error_as_txt}")
