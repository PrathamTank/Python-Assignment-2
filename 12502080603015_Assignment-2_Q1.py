import re
import os
from collections import defaultdict

def extract_emails(file_path):
    pattern = re.compile(
        r'(?<![A-Za-z0-9._+-])'
        r'[A-Za-z0-9+._-]+'
        r'@'
        r'[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*'
        r'\.(?:com|edu|org)'
        r'(?![A-Za-z0-9_-])',
        re.IGNORECASE
    )

    domain_emails = defaultdict(set)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            for match in pattern.finditer(line):
                email = match.group().lower()
                domain = email.split("@", 1)[1]
                domain_emails[domain].add(email)

    for domain in sorted(domain_emails):
        emails = domain_emails[domain]
        print(domain, len(emails), min(emails))


file_path = input("Enter text file path: ").strip()

if os.path.isfile(file_path):
    extract_emails(file_path)
else:
    print("ERROR: File not found")