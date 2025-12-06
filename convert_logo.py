"""
Script to convert logo to Python string for embedding
"""

import base64

with open('Images/badgersolarracing_logo.jpeg', 'rb') as f:
    logo_data = base64.b64encode(f.read()).decode('utf-8')
    
# Split into chunks for readability
chunk_size = 80
logo_chunks = [logo_data[i:i+chunk_size] for i in range(0, len(logo_data), chunk_size)]

print('LOGO_BASE64 = (')
for i, chunk in enumerate(logo_chunks):
    if i < len(logo_chunks) - 1:
        print(f'    "{chunk}"')
    else:
        print(f'    "{chunk}"')
print(')')
print(f'\n# Total length: {len(logo_data)} bytes')
