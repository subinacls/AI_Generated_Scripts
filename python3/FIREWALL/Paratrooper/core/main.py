import sys

# Ensuring input() works across both versions
try:
    input = raw_input  # In Python 2, raw_input() is used
except NameError:
    pass  # In Python 3, input() is already correct

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

##### SET DEBUG #####
bi.diag = True  # If True, diagnostics are enabled
