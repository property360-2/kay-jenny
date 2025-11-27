import re

file_path = r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\orders\views.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines before: {len(lines)}")

cleaned_lines = []
skip_until_closing = 0

for i, line in enumerate(lines):
    stripped = line.strip()

    # Skip orphaned lines that look like they're from removed AuditTrail calls
    if stripped.startswith("',") and i + 1 < len(lines):
        # Check if next lines are dict content
        next_line = lines[i+1].strip()
        if next_line.startswith('data_snapshot') or ('{' in next_line):
            print(f"Removing orphaned pattern starting at line {i+1}: {stripped[:50]}")
            skip_until_closing = 1  # Start skipping
            continue

    if skip_until_closing > 0:
        # Count braces to know when to stop skipping
        if '{' in stripped:
            skip_until_closing += 1
        if '}' in stripped:
            skip_until_closing -= 1

        if stripped == ')' and skip_until_closing == 1:
            skip_until_closing = 0  # Stop skipping after this line
            print(f"  Stopped skipping at line {i+1}")
        continue

    cleaned_lines.append(line)

print(f"Total lines after: {len(cleaned_lines)}")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print(f"Cleaned {file_path}")
