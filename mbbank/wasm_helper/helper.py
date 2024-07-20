import dataclasses
import json
import struct
import wasmtime


class Memory:
    def __init__(self, store_wasm, mem: wasmtime.Memory):
        self.store_wasm = store_wasm
        self.mem = mem
        self.wasm_page_size = 65536

    def read(self, start_address, end_address):
        return self.mem.read(self.store_wasm, start_address, end_address)

    def write(self, value, start_address):
        need = start_address + len(value)
        if self.mem.size(self.store_wasm) * self.wasm_page_size < need:
            print("need", need, "size", self.mem.size(self.store_wasm) * self.wasm_page_size)
            if self.wasm_page_size > need:
                grow_page = 1
            else:
                grow_page = int(need / self.wasm_page_size)
                if grow_page > int(grow_page):
                    grow_page += 1
            self.mem.grow(self.store_wasm, int(grow_page))
        return self.mem.write(self.store_wasm, value, start_address)

    def getBigInt64(self, address, littleEndian=False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<q', data)
        else:
            value, = struct.unpack('>q', data)
        return value

    def getBigUint64(self, address, littleEndian=False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<Q', data)
        else:
            value, = struct.unpack('>Q', data)
        return value

    def getFloat16(self, address, littleEndian=False):
        data = self.read(address, address + 2)
        value, = struct.unpack('<e', data)  # Replace '<e' with the correct format
        return value

    def getFloat32(self, address, littleEndian=False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<f', data)
        else:
            value, = struct.unpack('>f', data)
        return value

    def getFloat64(self, address, littleEndian=False):
        data = self.read(address, address + 8)
        if littleEndian:
            value, = struct.unpack('<d', data)
        else:
            value, = struct.unpack('>d', data)
        return value

    def getInt16(self, address, littleEndian=False):
        data = self.read(address, address + 2)
        if littleEndian:
            value, = struct.unpack('<h', data)
        else:
            value, = struct.unpack('>h', data)
        return value

    def getInt32(self, address, littleEndian=False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<i', data)
        else:
            value, = struct.unpack('>i', data)
        return value

    def getInt8(self, address, littleEndian=False):
        data = self.read(address, address + 1)
        value, = struct.unpack('b', data)
        return value

    def getUint16(self, address, littleEndian=False):
        data = self.read(address, address + 2)
        if littleEndian:
            value, = struct.unpack('<H', data)
        else:
            value, = struct.unpack('>H', data)
        return value

    def getUint32(self, address, littleEndian=False):
        data = self.read(address, address + 4)
        if littleEndian:
            value, = struct.unpack('<I', data)
        else:
            value, = struct.unpack('>I', data)
        return value

    def getUint8(self, address, littleEndian=False):
        data = self.read(address, address + 1)
        value, = struct.unpack('B', data)
        return value

    def setBigInt64(self, address, value, littleEndian=False):
        format_str = '<q' if littleEndian else '>q'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setBigUint64(self, address, value, littleEndian=False):
        format_str = '<Q' if littleEndian else '>Q'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setFloat16(self, address, value, littleEndian=False):
        format_str = '<e'  # Replace '<e' with the correct format
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setFloat32(self, address, value, littleEndian=False):
        format_str = '<f' if littleEndian else '>f'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setFloat64(self, address, value, littleEndian=False):
        format_str = '<d' if littleEndian else '>d'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setInt16(self, address, value, littleEndian=False):
        format_str = '<h' if littleEndian else '>h'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setInt32(self, address, value, littleEndian=False):
        format_str = '<i' if littleEndian else '>i'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setInt8(self, address, value, littleEndian=False):
        data = struct.pack('b', value)
        self.write(data, address)

    def setUint16(self, address, value, littleEndian=False):
        format_str = '<H' if littleEndian else '>H'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setUint32(self, address, value, littleEndian=False):
        value = int(value)
        value &= 0xFFFFFFFF
        format_str = '<I' if littleEndian else '>I'
        data = struct.pack(format_str, value)
        self.write(data, address)

    def setUint8(self, address, value, littleEndian=False):
        data = struct.pack('B', value)
        self.write(data, address)


class fs_object:
    def __init__(self):
        self.outputBuf = ""

        @dataclasses.dataclass(unsafe_hash=True)
        class constants_object:
            O_WRONLY: int
            O_RDWR: int
            O_CREAT: int
            O_TRUNC: int
            O_APPEND: int
            O_EXCL: int

        self.constants = constants_object(
            **{"O_WRONLY": -1, "O_RDWR": -1, "O_CREAT": -1, "O_TRUNC": -1, "O_APPEND": -1, "O_EXCL": -1})

    def enosys(self):
        raise NotImplementedError

    def writeSync(self, fd, buf: bytes):
        self.outputBuf += buf.decode()
        nl = self.outputBuf.rfind("\n")
        if nl != -1:
            print(self.outputBuf[:nl])
            self.outputBuf = self.outputBuf[nl + 1:]
        return len(buf)

    def write(self, fd, buf, offset, length, position, callback):
        n = self.writeSync(fd, buf)
        callback(None, n)

class process_object:
    def __init__(self):
        self.ppid = -1
        self.pid = -1
        pass

    def getuid(self):
        return -1

    def getgid(self):
        return -1

    def geteuid(self):
        return -1

    def getegid(self):
        return -1


class dict_warper:
    def __init__(self, dict_data):
        for key, value in dict_data.items():
            setattr(self, key, value)

    def to_dict(self):
        return {key: getattr(self, key) for key in dir(self) if not (key.startswith("__") or key == "to_dict")}


class hash_list(list):
    def __hash__(self):
        return hash(json.dumps(self))

    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default
