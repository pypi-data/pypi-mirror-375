# OSEF library

Library containing utilities to read and parse a stream, live or recorded, retrieved from
**Shift**.

The stream is in the **OSEF** format (**O**pen **SE**rialization **F**ormat):
it's an Outsight-defined serialisation binary format used to encode data streaming out of Shift. 
It is based on *TLV-encoding*.

For the full documentation, see: [Developer documentation](https://outsight-tech.gitlab.io/common/osef-python-library/).  
You can contact us @ https://support.outsight.ai

## Installation
Install from PyPi using pip:
```bash
pip install osef
``` 
## Usage

Open and parse an osef file or stream: 

```python
import osef

osef_path = "path/to/my/file.osef"
# or osef_path="tcp://192.168.2.2:11120"

for frame_dict in osef.parse(osef_path):
    print(frame_dict)
```

Additional parameters:
- `first`/`last`: the first and the last frame to parse
- `auto_reconnect`: enable parser auto_reconnection (default: `True`)
- `real_frequency`: If False, parse data as fast as your computer can. If True, process the data as the same pace as the real time stream from Shift (default: `False`)
- `lazy`: If lazy, the dict only unpack the values when they are accessed to save up resources (default: `True`)


To find more code samples, see [Outsight Code Samples repository](https://gitlab.com/outsight-public/outsight-code-samples/-/tree/master).