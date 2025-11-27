import re

# Files to process
files_to_clean = [
    r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\products\views.py',
    r'C:\Users\Administrator\Desktop\projects\kay-jenny\kay-jenny\sales_inventory_system\accounts\views.py',
]

def clean_audit_trail(file_path):
    """Remove all AuditTrail references from a file"""
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove AuditTrail import statements
    content = re.sub(r'^\s*from\s+sales_inventory_system\.system\.models\s+import\s+AuditTrail\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*from\s+\.\.system\.models\s+import\s+AuditTrail\s*$', '', content, flags=re.MULTILINE)

    # Remove AuditTrail.objects.create() blocks (including multi-line)
    # Pattern: match from "AuditTrail.objects.create(" to the closing ")"
    pattern = r'^\s*#?\s*.*?AuditTrail\.objects\.create\([^)]*?\)[\s\n]*'
    content = re.sub(pattern, '', content, flags=re.MULTILINE)

    # More aggressive pattern for nested parentheses
    pattern2 = r'AuditTrail\.objects\.create\((?:[^()]*|\([^()]*\))*\)'
    content = re.sub(pattern2, '', content)

    # Remove comment lines about audit trail
    content = re.sub(r'^\s*#\s*Create audit (log|trail).*$', '', content, flags=re.MULTILINE)

    # Remove audit_trails list declarations and bulk_create
    content = re.sub(r'^\s*audit_trails\s*=\s*\[.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*audit_trails\.append\([^\]]*?\).*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*AuditTrail\.objects\.bulk_create\(.*\).*$', '', content, flags=re.MULTILINE)

    # Clean up excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Cleaned {file_path}")

# Process all files
for file_path in files_to_clean:
    try:
        clean_audit_trail(file_path)
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
