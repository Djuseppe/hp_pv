from influxdb import DataFrameClient


def main():
    # host = 'localhost'
    # port = 8086
    dbname = 'uceeb'
    protocol = 'line'
    measurement = 'pv_measurement'

    client = DataFrameClient(
        host=r'10.208.8.93', port=8086,
        username='eugene', password='7vT4g#1@K',
        database=dbname
    )

    res = client.query("select * from {}".format(measurement), database=dbname)
    print(res)


if __name__ == '__main__':
    main()
