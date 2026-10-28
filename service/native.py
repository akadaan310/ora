"""Optional C ABI bridge; C++ remains the source of deterministic primitive operations."""
import ctypes, json
from pathlib import Path

LIBRARY = Path(__file__).resolve().parents[1]/'build'/'libora.so'
class NativeKernel:
    def __init__(self,path=LIBRARY):
        self.lib=ctypes.CDLL(str(path))
        self.lib.ora_scene.argtypes=[ctypes.c_uint64,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
        self.lib.ora_scene.restype=ctypes.c_size_t
        self.lib.ora_inspect.argtypes=[ctypes.c_char_p,ctypes.c_void_p,ctypes.c_size_t]
        self.lib.ora_inspect.restype=ctypes.c_size_t
        self.lib.ora_compile.argtypes=[ctypes.c_char_p,ctypes.c_void_p,ctypes.c_size_t]
        self.lib.ora_compile.restype=ctypes.c_int
    def _two_pass(self,func,*args):
        n=func(*args,None,0)
        if n>8_000_000:raise ValueError('native output exceeds budget')
        buf=ctypes.create_string_buffer(n+1)
        actual=func(*args,buf,len(buf))
        if actual!=n:raise ValueError('native response length mismatch')
        return json.loads(buf.value)
    def scene(self,seed,count):return self._two_pass(self.lib.ora_scene,seed,count)
    def inspect(self,text):return self._two_pass(self.lib.ora_inspect,text.encode())
    def compile(self,text):
        buf=ctypes.create_string_buffer(2048)
        ok=self.lib.ora_compile(text.encode(),buf,len(buf))
        return {'admitted_syntax':bool(ok),'result':json.loads(buf.value)}
