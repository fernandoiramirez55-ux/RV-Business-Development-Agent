import os
from anthropic import Anthropic

api_key = os.environ.get('ANTHROPIC_API_KEY')
print(f'API Key found: {api_key[:10] if api_key else "NOT FOUND"}')

if api_key:
    try:
        client = Anthropic(api_key=api_key)
        print('Client created successfully')
    except Exception as e:
        print(f'Error creating client: {e}')
else:
    print('No API key in environment')