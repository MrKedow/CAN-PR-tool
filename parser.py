import cantools
import re
from database import init_db, insert_signal

db = cantools.database.load_file('example.dbc')
init_db()

# 解析 asc 格式日志
def parse_asc(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            # 匹配 CAN 数据行：时间戳 总线 消息ID Rx d 8 数据字节...
            m = re.match(r'\s*(\d+\.\d+)\s+\d+\s+(\d+)\s+Rx\s+d\s+\d+\s+([0-9A-Fa-f ]+)', line)
            if m:
                timestamp = float(m.group(1))
                msg_id = int(m.group(2))
                data_str = m.group(3).replace(' ', '')
                data = bytes.fromhex(data_str)
                # 查找对应的 DBC 消息定义
                try:
                    msg = db.get_message_by_frame_id(msg_id)
                except KeyError:
                    continue
                signals = msg.decode(data)
                for sig_name, sig_value in signals.items():
                    insert_signal(timestamp, msg_id, sig_name, sig_value)
                    print(f"{timestamp:.6f} : {sig_name} = {sig_value}")

if __name__ == '__main__':
    parse_asc('trace.asc')