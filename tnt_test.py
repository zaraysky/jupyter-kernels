import tarantool

connection = tarantool.connect(
    host='localhost',
    port=3300,
    user='guest')
response = connection.eval("return XXXX(2)")

#
# response = connection.call("XXX(2)")

print(response.__dict__)
connection.close()

