import context
import importlib_resources as ir 
with ir.open_text('e340py','VERSION') as f:
    version=f.read().strip()
    
import e340py
print(f'e340py.__version__ {e340py.__version__}')
