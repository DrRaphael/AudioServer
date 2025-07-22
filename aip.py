import time

from pymodbus.client import ModbusSerialClient
import logging

# 配置日志（可选，用于调试）
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


def connect_modbus(port='/dev/ttyUSB0', baudrate=9600, timeout=1):
    """创建并初始化Modbus RTU客户端连接"""
    try:
        # 创建Modbus RTU客户端
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            parity='N',
            stopbits=1,
            bytesize=8,
        )

        # 连接到从站设备
        if client.connect():
            print(f"成功连接到Modbus RTU设备: {port}")
            return client
        else:
            print(f"无法连接到Modbus RTU设备: {port}")
            return None
    except Exception as e:
        print(f"连接时发生错误: {e}")
        return None


def read_holding_registers(client, slave_id=1, address=0, count=10):
    """读取保持寄存器"""
    if not client:
        return None

    try:
        # 发送读保持寄存器请求
        result = client.read_holding_registers(
            address=address,
            count=count,
            slave=slave_id  # pymodbus 3.0+ 使用 slave 参数而非 unit
        )

        # 检查是否有异常
        if result.isError():
            print(f"读取保持寄存器时发生异常: {result}")
            return None

        # 返回寄存器值
        return result.registers
    except Exception as e:
        print(f"读取保持寄存器时发生错误: {e}")
        return None


def write_single_register(client, slave_id=1, address=0, value=0):
    """写入单个保持寄存器"""
    if not client:
        return False

    try:
        # 发送写单个寄存器请求
        result = client.write_register(
            address=address,
            value=value,
            slave=slave_id  # pymodbus 3.0+ 使用 slave 参数而非 unit
        )

        # 检查是否有异常
        if result.isError():
            print(f"写入单个寄存器时发生异常: {result}")
            return False

        # 写入成功
        return True
    except Exception as e:
        print(f"写入单个寄存器时发生错误: {e}")
        return False


def close_connection(client):
    """关闭Modbus连接"""
    if client:
        client.close()
        print("Modbus连接已关闭")


if __name__ == "__main__":
    # 配置参数
    PORT = 'COM3'  # 根据实际情况修改串口设备
    BAUDRATE = 115200  # 波特率，需与从站设备匹配

    current = 1
    # 连接到Modbus设备
    modbus_client = connect_modbus(port=PORT, baudrate=BAUDRATE)
    while True:
        current *= 10
        current_str = f"Current: {current}                  "
        # 将字符串顺序写入0-16号寄存器,左对齐,填充空格
        for i in range(16):
            write_single_register(modbus_client, 1, i, value=ord(current_str[i]))
        write_single_register(modbus_client, 1, 20, 1)
        time.sleep(0.01)