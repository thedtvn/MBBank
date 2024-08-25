import asyncio
import json
import math
import os
import time
import traceback
import wasmtime
from .helper import Memory, fs_object, process_object, dict_warper, hash_list
from contextvars import ContextVar

undefined = ContextVar('undefined')


class globalThis:
    def __init__(self):
        self.exports = undefined
        self.window = dict_warper({"document": dict_warper({})})
        self.fs = fs_object()
        self.process = process_object()
        self.location = dict_warper({"origin": "https://online.mbbank.com.vn"})

    def __getattribute__(self, item):
        if item == "Object":
            return object
        elif item == "Array":
            return list
        elif item == "Uint8Array":
            return bytes
        return object.__getattribute__(self, item)


global_this = globalThis()


class GO:
    def __init__(self, wasm_store):
        self.wasm_store = wasm_store
        self.argv = ["js"]
        self.env = {}
        self._exitPromise = asyncio.Event()
        self._pendingEvent = None
        self._scheduledTimeouts = {}
        self._nextCallbackTimeoutID = 1
        self.go_js = GOJS(self)

        def setInt64(addr, v):
            self.mem.setUint32(addr + 0, v, True)
            self.mem.setUint32(addr + 4, math.floor(v / 4294967296), True)

        self.setInt64 = setInt64

        def getInt64(addr):
            low = self.mem.getUint32(addr + 0, True)
            high = self.mem.getInt32(addr + 4, True)
            return low + high * 4294967296

        self.getInt64 = getInt64

        def loadValue(addr):
            f = self.mem.getFloat64(addr, True)
            if f == 0:
                return
            elif not math.isnan(f):
                return f
            aid = self.mem.getInt32(addr, True)
            return self._values[aid]

        self.loadValue = loadValue

        def storeValue(addr, v=undefined):
            nanHead = 0x7FF80000
            if type(v) in [int, float] and v != 0:
                if math.isnan(v):
                    self.mem.setInt32(addr + 4, nanHead, True)
                    self.mem.setFloat64(addr, 0, True)
                    return
                self.mem.setFloat64(addr, v, True)
                return

            if v is undefined:
                self.mem.setFloat64(addr, 0, True)
                return

            obj_id = self._ids.get(v, undefined)

            if obj_id == undefined:
                if self._idPool:
                    obj_id = self._idPool.pop()
                else:
                    obj_id = len(self._values)
                if obj_id >= len(self._values):
                    self._values.extend([undefined for _ in range(obj_id - len(self._values) + 1)])
                if obj_id >= len(self._goRefCounts):
                    self._goRefCounts.extend([float("inf") for _ in range(obj_id - len(self._goRefCounts) + 1)])
                self._values[obj_id] = v
                self._goRefCounts[obj_id] = 0
                self._ids.setdefault(v, obj_id)

            self._goRefCounts[obj_id] += 1
            typeFlag = 1  # everything is an object
            if v is None:
                typeFlag = 0
            elif type(v) is str:
                typeFlag = 2
            # elif type(v) is symbol: # symbol is not supported in python
            #    typeFlag = 3
            elif callable(v):
                typeFlag = 4
            self.mem.setInt32(addr + 4, nanHead | typeFlag, True)
            self.mem.setInt32(addr, obj_id, True)

        self.storeValue = storeValue

        def loadSlice(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return self.mem.read(array, array + len_read), array, len_read

        self.loadSlice = loadSlice

        def loadSliceOfValues(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return [self.loadValue(array + i * 8) for i in range(len_read)]

        self.loadSliceOfValues = loadSliceOfValues

        def loadString(addr):
            array = getInt64(addr + 0)
            len_read = getInt64(addr + 8)
            return self.mem.read(array, array + len_read).decode("utf-8")

        self.loadString = loadString

    @classmethod
    def exit_process(cls, exitCode):
        print("exit code:", exitCode)

    def importObject(self, imports_type: list[wasmtime.ImportType]):
        def proxy(name):
            def fn(*args, **kwargs):
                call = getattr(self.go_js, name)
                return call(*args, **kwargs)

            return fn

        return [wasmtime.Func(self.wasm_store, i.type, proxy(i.name)) for i in imports_type]

    # noinspection PyAttributeOutsideInit
    def run(self, inst):
        self._inst = inst
        self.mem = Memory(self.wasm_store, inst["mem"])
        self._values = [
            float("nan"),
            0,
            None,
            True,
            False,
            global_this,
            self
        ]
        self._goRefCounts = [float("inf") for _ in range(50)]
        self._ids = dict(
            [
                (0, 1),
                (None, 2),
                (True, 3),
                (False, 4),
                (global_this, 5),
                (self, 6),
            ]
        )
        self._idPool = []
        self.exited = False
        self.offset = 4096

        def strPtr(str_data: str):
            ptr = self.offset
            bytes_data = (str_data + "\0").encode()
            self.mem.write(bytes_data, self.offset)
            self.offset += len(bytes_data)
            if (self.offset % 8) != 0:
                self.offset += 8 - (self.offset % 8)
            return ptr

        argc = len(self.argv)
        argvPtrs = []
        [argvPtrs.append(strPtr(i)) for i in self.argv]
        argvPtrs.append(0)
        envKeys = sorted(self.env.keys(), key=str)
        [argvPtrs.append(strPtr(f"{i}={self.env[i]}")) for i in envKeys]
        argvPtrs.append(0)
        argv = self.offset
        for ptr in argvPtrs:
            self.mem.setUint32(self.offset, ptr, True)
            self.mem.setUint32(self.offset + 4, 0, True)
            self.offset += 8
        wasmMinDataAddr = 4096 + 8192
        if self.offset >= wasmMinDataAddr:
            raise MemoryError("total length of command line and environment variables exceeds limit")
        self.go_js.run_init()
        self._inst["run"](self.wasm_store, argc, argv)
        if self.exited:
            self._exitPromise.set()

    def _resume(self):
        if self.exited:
            self._exitPromise.set()
            raise RuntimeError("Go program has already exited")
        self._inst["resume"](self.wasm_store)
        if self.exited:
            self._exitPromise.set()

    def _makeFuncWrapper(self, ids):
        def wrapper(*args, **kwargs):
            event = dict_warper({"id": int(ids), "args": hash_list(args), "this": global_this})
            self._pendingEvent = event
            self._resume()
            return event.result

        return wrapper


# noinspection PyAttributeOutsideInit
class GOJS:
    def __init__(self, go_obj: GO):
        self.go = go_obj

    def run_init(self):
        self.mem = self.go.mem

    def __getattribute__(self, item):
        if item.startswith("runtime."):
            item = item.replace("runtime.", "rt_")
        elif item.startswith("syscall/js."):
            item = item.replace("syscall/js.", "sysjs_")
        data = object.__getattribute__(self, item)
        return data

    def rt_wasmExit(self, sp):
        code = self.mem.getInt32(sp + 8, True)
        self.go.exited = True
        self.go._exitPromise.set()
        self.go.exit_process(code)

    def rt_wasmWrite(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        fd = self.go.getInt64(sp + 8)
        p = self.go.getInt64(sp + 16)
        n = self.mem.getInt32(sp + 24, True)
        global_this.fs.writeSync(fd, self.mem.read(p, p + n))

    def rt_resetMemoryDataView(self, address):
        # do nothing maybe ?
        pass

    def rt_nanotime1(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        self.go.setInt64(sp + 8, int(time.time() * 1000) * 1000000)

    def rt_walltime(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        msec = int(time.time() * 1000)
        self.go.setInt64(sp + 8, msec / 1000)
        self.mem.setInt32(sp + 16, (msec % 1000) * 1000000, True)

    def rt_scheduleTimeoutEvent(self, *args):
        pass

    def rt_clearTimeoutEvent(self, *args):
        pass

    def rt_getRandomData(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        byte_aray, start, length = self.go.loadSlice(sp + 8)
        random_data = os.urandom(length)
        self.mem.write(random_data, start)

    def sysjs_finalizeRef(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        ids = self.mem.getUint32(sp + 8, True)
        if self.go._goRefCounts[ids] == 0:
            v = self.go._values[ids]
            self._values[ids] = None
            self.go._ids.pop(v, None)
            self.go._idPool.append(ids)

    def sysjs_stringVal(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        data = self.go.loadString(sp + 8)
        self.go.storeValue(sp + 24, data)

    def sysjs_valueGet(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        obj = self.go.loadValue(sp + 8)
        name = self.go.loadString(sp + 16)
        if type(obj) is dict:
            result = obj.get(name, undefined)
        else:
            result = getattr(obj, name)
        sp = self.go._inst["getsp"](self.go.wasm_store) >> 0
        self.go.storeValue(sp + 32, result)

    def sysjs_valueSet(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        setattr(self.go.loadValue(sp + 8), self.go.loadString(sp + 16), self.go.loadValue(sp + 32))

    def sysjs_valueDelete(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        delattr(self.go.loadValue(sp + 8), self.go.loadString(sp + 16))

    def sysjs_valueIndex(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        obj = self.go.loadValue(sp + 8)
        int_data = self.go.getInt64(sp + 16)
        result = obj.get(int_data, undefined)
        self.go.storeValue(sp + 24, result)

    def sysjs_valueSetIndex(self, *args):
        pass

    def sysjs_valueCall(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        try:
            v = self.go.loadValue(sp + 8)
            m = getattr(v, self.go.loadString(sp + 16))
            args = self.go.loadSliceOfValues(sp + 32)
            result = m(*args)
            sp = self.go._inst["getsp"](self.go.wasm_store) >> 0
            self.go.storeValue(sp + 56, result)
            self.mem.setUint8(sp + 64, 1)
        except Exception as e:
            traceback.print_exc()
            sp = self.go._inst["getsp"](self.go.wasm_store) >> 0
            self.go.storeValue(sp + 56, e)
            self.mem.setUint8(sp + 64, 0)

    def sysjs_valueInvoke(self, *args):
        pass

    def sysjs_valueNew(self, *args):
        pass

    def sysjs_valueLength(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        self.go.setInt64(sp + 16, len(self.go.loadValue(sp + 8)))

    def sysjs_valuePrepareString(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        data = self.go.loadValue(sp + 8)
        if type(data) is float:
            data = int(data)
        str_data = str(data).encode('utf-8')
        self.go.storeValue(sp + 16, str_data)
        self.go.setInt64(sp + 24, len(str_data))

    def sysjs_valueLoadString(self, sp):
        sp = (sp >> 0) & 0xFFFFFFFF
        str_data = self.go.loadValue(sp + 8)
        byte_aray, start, length = self.go.loadSlice(sp + 16)
        self.mem.write(str_data, start)

    def sysjs_valueInstanceOf(self, *args):
        pass

    def sysjs_copyBytesToGo(self, *args):
        pass

    def sysjs_copyBytesToJS(self, *args):
        pass

    def debug(self, *args):
        pass


def wasm_encrypt(wasm_files, json_data):
    if getattr(global_this, 'bder', None) is not None:
        return global_this.bder(json.dumps(json_data), "0")
    engine = wasmtime.Engine()
    modun = wasmtime.Module(engine, wasm_files)
    store = wasmtime.Store(engine)
    go_obj = GO(store)
    instance = wasmtime.Instance(store, modun, imports=go_obj.importObject(modun.imports))
    run_as_lib = instance.exports(store)
    go_obj.run(run_as_lib)
    return global_this.bder(json.dumps(json_data), "0")