import re

files = [
    r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\products\views.py',
]

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip lines that are just orphaned braces/parentheses
        stripped = line.strip()
        if stripped in ['}', ')', '},', '),', '})', '})']:
            print(f"Removing orphaned '{stripped}' at line {i+1}")
            # Check if next line is also orphaned
            if i + 1 < len(lines) and lines[i+1].strip() in ['}', ')', '),']:
                skip_next = True
            continue

        if skip_next:
            if stripped in ['}', ')', '),']:
                print(f"Removing orphaned '{stripped}' at line {i+1}")
                continue
            skip_next = False

        # Remove lines that are just a comma
        if stripped == ',':
            print(f"Removing orphaned comma at line {i+1}")
            continue

        cleaned_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

    print(f"Cleaned {file_path}")
