import cantools
import can
from database import insert_signal, init_db
import time

db = cantools.database.load_file('example.dbc')
init_db()

bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
print("开始记录 vcan0 报文，按 Ctrl+C 停止。")
try:
    for msg in bus:
        try:
            signals = db.decode_message(msg.arbitration_id, msg.data)
            ts = time.time()
            for name, val in signals.items():
                insert_signal(ts, msg.arbitration_id, name, val)
                print(f"{ts:.6f} ID=0x{msg.arbitration_id:X} {name}={val}")
        except KeyError:
            pass
except KeyboardInterrupt:
    print("停止记录。")