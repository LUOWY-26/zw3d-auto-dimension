import os
import ctypes

def Load_ZW3D(dll_path=r"C:\Users\gyj15\Desktop\zw3d\ZW3D_DLL\Z3Demo.dll"):
    dll = ctypes.CDLL(dll_path)
    print("DLL加载成功", dll)

    dll.MyCustomFunc.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    dll.MyCustomFunc.restype = ctypes.c_int
    test_result = dll.MyCustomFunc(10, 20, "invoke successfully".encode("utf-8"))
    print(test_result)
    return test_result

if __name__ == "__main__":
    Load_ZW3D()