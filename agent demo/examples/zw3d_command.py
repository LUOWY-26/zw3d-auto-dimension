"""Simple example of using Deepseek Reasoner to run ZW3D command."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.deepseek_wrapper import DeepseekToolWrapper
from tools.zw3d_command_tool import ZW3DCommandTool, ZW3DCommandOpen, ZW3DCommandExpPDF
import time


def print_response(step: str, response: str):
    """Print formatted response from Deepseek."""
    print(f"\n{'=' * 80}")
    print(f"STEP: {step}")
    print(f"{'=' * 80}")
    print(response)
    print(f"{'=' * 80}\n")


def main():
    """Run a simple demonstration."""
    try:
        print("Initializing Deepseek...")
        wrapper = DeepseekToolWrapper()
        # computer = ComputerTool()
        command = ZW3DCommandTool()
        open_c = ZW3DCommandOpen()
        expPdf_c = ZW3DCommandExpPDF()
        wrapper.register_tool(command)
        wrapper.register_tool(open_c)
        wrapper.register_tool(expPdf_c)

        print("\nStarting demo in 3 seconds...")
        time.sleep(3)

        # execute command
        result = wrapper.execute("在ZW3D打开文件'C:/Users/gyj15/AppData/Roaming/ZWSOFT/ZW3D/ZW3D 2905/output/archive/a.Z3PRT'。")
        print_response("ZW3D COMMAND STEP-1", result)
        time.sleep(0.5)
        result = wrapper.execute("导出'OBJECT'类型的PDF文件到'C:/Users/gyj15/Desktop/zw3d/export/file.pdf'。")
        print_response("ZW3D COMMAND STEP-2", result)
        print("end process...")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Your .env file has DEEPSEEK_API_KEY")
        print("2. All dependencies are installed")


if __name__ == "__main__":
    main()