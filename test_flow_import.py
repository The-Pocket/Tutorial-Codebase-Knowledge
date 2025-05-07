"""Simple script to test pocketflow Flow imports."""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import pocketflow
    print(f"Successfully imported pocketflow")
    print(f"pocketflow path: {pocketflow.__file__}")
    
    # Get all attributes of pocketflow
    print(f"\nAttributes of pocketflow:")
    for attr in dir(pocketflow):
        if not attr.startswith('__'):
            print(f"- {attr}")
    
    try:
        from pocketflow import Flow
        print(f"\nSuccessfully imported Flow from pocketflow")
        print(f"Flow is: {Flow}")
    except ImportError as e:
        print(f"\nFailed to import Flow from pocketflow: {e}")
except ImportError as e:
    print(f"Failed to import pocketflow: {e}")

print("\nDone.")
