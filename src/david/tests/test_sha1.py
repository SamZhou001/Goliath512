from pprint import pprint
from david.utils import digest

def generate_constant_sha1(num):
    return [digest(str(i)) for i in range(num)]

if __name__ == '__main__':
    pprint(generate_constant_sha1(6))
