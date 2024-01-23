from pyModbusTCP.client import ModbusClient
from time import sleep, perf_counter
from json import load
from statistics import stdev
from sys import stderr

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

durations = []

def run():
    # create ModbusTCP client (master)
    print(f"Connecting to {MODBUS_TCP_HOST}:{MODBUS_TCP_PORT}, unit-ID {MODBUS_TCP_ID}...")
    c = ModbusClient(host=MODBUS_TCP_HOST, port=config["modbus_tcp"]["port"], unit_id=config["modbus_tcp"]["id"], auto_open=True)
    if c.open():
        # let everything settle for a moment
        print("Connection successful", file=stderr)
        print("Waiting for things to settle (sleep)...", file=stderr)
        sleep(5)

        # benchmark reading & writing
        print(f"Performing {NUM_ITERATIONS} read-write cycles...", file=stderr)
        
        last_written_coils = None
        last_written_hregs = None
        for i in range(0, NUM_ITERATIONS):
            start_time = perf_counter()

            # read
            coils = c.read_coils(0, NUM_REGS)        
            if not coils:
                raise Exception(c.last_error_as_txt)
            if last_written_coils is not None and coils != last_written_coils:
                raise Exception("Read back coils didn't match")
            hregs = c.read_holding_registers(0, NUM_REGS)
            if not hregs:
                raise Exception(c.last_error_as_txt)
            if last_written_hregs is not None and hregs != last_written_hregs:
                raise Exception("Read back hregs didn't match")
            iregs = c.read_input_registers(0, NUM_REGS)
            if not iregs:
                raise Exception(c.last_error_as_txt)
            dis = c.read_discrete_inputs(0, NUM_REGS)
            if not dis:
                raise Exception(c.last_error_as_txt)
            
            # write
            for j in range(len(hregs)):
                hregs[j] = (hregs[j] + 1) % 0xFF
            if not c.write_multiple_registers(0, hregs):
                raise Exception(c.last_error_as_txt)    
            last_written_hregs = hregs.copy()
            for j in range(len(coils)):
                coils[j] = not coils[j]                
            if not c.write_multiple_coils(0, coils):
                raise Exception(c.last_error_as_txt)
            last_written_coils = coils.copy()
            
            duration = perf_counter() - start_time
            durations.append(duration)
        
        c.close()
        print(f"Done")
    else:
        print(f"Error opening modbus connection: {c.last_error_as_txt}", file=stderr)

try:
    run()
except BaseException as ex:
    print(f"Error after cycle {len(durations)}/{NUM_ITERATIONS} ({len(durations)/NUM_ITERATIONS * 100:.0f} %)\n{str(ex)}", file=stderr)

if (len(durations) <= 0):
    print("No results obtained", file=stderr)
    exit(1)

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