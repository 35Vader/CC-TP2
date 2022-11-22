import parser
import json

configFile = ""#input()
if configFile == "":
    configFile = "dns/dnsFiles/config.txt"


config = parser.parserConfig(configFile)
db = parser.parserDataBase(config['DB'][0]['value'])




def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d

bin = dict_to_binary(db)
print(bin)

dct = binary_to_dict(bin)
print(dct)