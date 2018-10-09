import context
import importlib_resources as ir 
with ir.open_text('e340py','VERSION') as f:
    version=f.read().strip()

print(f'accessed VERSION: {version}')
    
import e340py
print(f'e340py.__version__ {e340py.__version__}')

print(e340py.version_file)
