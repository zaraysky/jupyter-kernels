import tarantool
import pprint
import json

connection = tarantool.connect(
    host='localhost',
    port=3300,
    user='guest')
cmd = 'arr = {a = 1; b=2}; return arr'

response = connection.eval(f"""
local f = loadstring([[{cmd}]])
local status, err = pcall(f)

return status, err""")

print(json.dumps(response._data[1], indent=4, sort_keys=True))

connection.close()

