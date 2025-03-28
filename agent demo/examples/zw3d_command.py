"""Simple example of using Deepseek Reasoner to run ZW3D command."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.deepseek_wrapper import DeepseekToolWrapper
from tools.zw3d_command_tool import ZW3DCommandTool
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
        wrapper.register_tool(command)

        print("\nStarting demo in 3 seconds...")
        time.sleep(3)

        # Move mouse
        result = wrapper.execute("Firstly, I need open a part in ZW3D, so run command 'FILEOPEN', and params has one element, named 'filePath', value is 'a.Z3PRT'")
        print_response("ZW3D COMMAND 1", result)
        time.sleep(0.5)
        result = wrapper.execute("And then run ZW3D command name 'EXPPDF', and params is a json data, the first one named 'path', "
                                 "value is 'C:/Users/gyj15/Desktop/zw3d/export/file.pdf'. And the second parameter named 'pdfType', value is 2. ")
        print_response("ZW3D COMMAND 2", result)
        print("end process...")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Your .env file has DEEPSEEK_API_KEY")
        print("2. All dependencies are installed")


if __name__ == "__main__":
    main()