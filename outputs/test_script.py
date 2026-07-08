import sys
import os

# Test script to verify Python can write to files
with open(r'C:\MRE\outputs\test_script_output.txt', 'w') as f:
    f.write('Python script executed successfully\n')
    f.write(f'CWD: {os.getcwd()}\n')
    f.write(f'Files in CWD: {os.listdir(".")[:10]}\n')
