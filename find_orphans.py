import re

files = [
    r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\products\views.py',
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"\n=== {file_path} ===")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Look for lines that are just orphaned syntax elements
        if stripped in ['}', ')', '},', '),', '})', '})', ','] or (stripped == ',' and i < len(lines)):
            print(f"Line {i}: '{stripped}'")
            # Show context
            start = max(0, i-3)
            end = min(len(lines), i+2)
            print("  Context:")
            for j in range(start, end):
                marker = ">>>" if j == i-1 else "   "
                print(f"    {marker} {j+1}: {lines[j].rstrip()}")
            print()
