__version__ = '0.1.6'

import pkgutil
import pandas as pd # type: ignore
from io import StringIO  # noqa: F401

def load_dataset(file_name):
    data = pkgutil.get_data('phenofect', f'Data/{file_name}')
    if data is None:
        raise FileNotFoundError(f"File '{file_name}' does not exist in the Data directory.")
    return pd.read_csv(StringIO(data.decode('utf-8')))

