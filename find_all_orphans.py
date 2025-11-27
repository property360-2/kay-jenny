import re

file_path = r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\orders\views.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"\n=== Suspicious lines in orders/views.py ===\n")
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    # Look for lines that are likely orphaned from AuditTrail calls
    if (stripped in ['}', ')', ',', '},', '),']) or \
       (stripped.startswith("',") and len(stripped) < 5) or \
       (stripped.startswith('",')):
        print(f"Line {i}: '{stripped}'")
        # Show context
        start = max(0, i-4)
        end = min(len(lines), i+3)
        print("  Context:")
        for j in range(start, end):
            marker = ">>>" if j == i-1 else "   "
            print(f"    {marker} {j+1}: {lines[j].rstrip()}")
        print()
