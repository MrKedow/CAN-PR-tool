import time
import cantools
import can
from database import init_db
import sqlite3

db = cantools.database.load_file('example.dbc')

def replay():
    conn = sqlite3.connect('can_data.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT timestamp, message_id FROM can_signals ORDER BY timestamp")
    rows = c.fetchall()
    if not rows:
        print("数据库为空，无法回灌。")
        return

    with can.interface.Bus(channel='vcan0', bustype='socketcan') as bus:
        prev_ts = None
        base_time = time.time()
        for ts, msg_id in rows:
            # 获取该时间戳下该报文的所有信号
            c2 = conn.cursor()
            c2.execute("SELECT signal_name, value FROM can_signals WHERE timestamp=? AND message_id=?", (ts, msg_id))
            signals = {name: val for name, val in c2.fetchall()}
            try:
                msg_def = db.get_message_by_frame_id(msg_id)
                data = msg_def.encode(signals)
                can_msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=False)
                # 计算延时（模拟原始时间间隔）
                if prev_ts is not None:
                    delay = ts - prev_ts
                    if delay > 0:
                        time.sleep(delay)
                else:
                    delay = 0
                bus.send(can_msg)
                print(f"Sent: ID=0x{msg_id:X}, data={data.hex()}, delay={delay:.3f}s")
                prev_ts = ts
            except Exception as e:
                print(f"Error encoding 0x{msg_id:X}: {e}")
    conn.close()

if __name__ == '__main__':
    replay()