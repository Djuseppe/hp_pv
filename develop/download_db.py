from lib.influx.influx_lib import DBReader
from lib.modbus_lib import ModbusClient


def main():
    db = DBReader()
    hp = ModbusClient()
    pv_power, res = db.get_data_from_db()


if __name__ == '__main__':
    main()
