[![PyPI version](https://badge.fury.io/py/pygenieacs.svg)](https://pypi.org/project/pygenieacs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# pygenieacs

A Python API client for [GenieACS](https://genieacs.com) — a TR-069 / CWMP Auto-Configuration Server.  
This library provides a simple interface to interact with the GenieACS **REST API**.

---

## ✨ Features
- List, inspect, and delete devices
- Run tasks (reboot, factory reset, firmware upgrade, etc.)
- Manage presets
- Manage provisions
- Simple, Pythonic interface

---

## 📦 Installation

```python
pip install pygenieacs
```
🚀 Usage

Initialize Client
```python
from pygenieacs import GenieACSClient, DevicesAPI, TasksAPI

# Connect to your GenieACS server
client = GenieACSClient(base_url="http://localhost:7557")

devices = DevicesAPI(client)
tasks = TasksAPI(client)

```

List Devices
```python
print(devices.list())
```

Get Device Details
```python
device_id = "001A2B3C4D"
print(devices.get(device_id))
```
Reboot a Device
```python
tasks.add(device_id, "reboot")
```
⚙️ Advanced
Presets
```python
from pygenieacs import PresetsAPI

presets = PresetsAPI(client)
presets.create("daily-reboot", {
    "weight": 0,
    "precondition": "true", # all devices
    "configurations": [
        {"parameter": "InternetGatewayDevice.ManagementServer.PeriodicInformInterval", "value": "60"}
    ]
})

```
Here’s a preset that applies a provision only if the device vendor is MikroTik:
```python
from pygenieacs import PresetsAPI

presets = PresetsAPI(client)

presets.create("mikrotik-provision", {
    "weight": 1,
    "precondition": "DeviceId.Manufacturer == 'MikroTik'",
    "configurations": [],
    "provisions": ["default-config"],  
})

```
See [mikrotik-provision](#mikrotik-provision) below.

This preset matches devices running firmware lower than v6.48 and applies a firmware upgrade task:
```python
from pygenieacs import PresetsAPI

presets = PresetsAPI(client)

presets.create("firmware-upgrade", {
    "weight": 10,
    "precondition": "Device.DeviceInfo.SoftwareVersion < '6.48'",
    "configurations": [],
    "provisions": ["upgrade-firmware"],
})

```
This preset applies only to devices with OUI 001A2B (common for vendor-specific CPEs)/MAC prefix:
```python
from pygenieacs import PresetsAPI

presets = PresetsAPI(client)

presets.create("oui-target", {
    "weight": 5,
    "precondition": "DeviceId.OUI == '001A2B'",
    "configurations": [
        {
            "parameter": "InternetGatewayDevice.LANDevice.1.LANHostConfigManagement.DHCPServerEnable",
            "value": False
        }
    ],
    "provisions": [],
})

```
Provisions
Here’s how to create a provision that ensures TR-069 Inform Interval is set correctly and also pushes a default Wi-Fi SSID.
### mikrotik-provision
```python

from pygenieacs import ProvisionsAPI

provisions = ProvisionsAPI(client)

#Ensure inform interval is set to 300 seconds (5 min)
#Set default Wi-Fi SSID if missing
script = """
let interval = declare("InternetGatewayDevice.ManagementServer.PeriodicInformInterval", {value: 1});
if (interval.value[0] != 300) {
  declare("InternetGatewayDevice.ManagementServer.PeriodicInformInterval", null, {value: 300});
}

let ssid = declare("InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.SSID", {value: 1});
if (!ssid.value[0]) {
  declare("InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.SSID", null, {value: "MyDefaultSSID"});
}
"""

# Upload provision to GenieACS
provisions.create("default-config", script)

```
🛠 Development
Clone the repo and install locally:
```python
git clone https://github.com/uberkie/pygenieacs.git
cd pygenieacs
pip install -e .
```
Run tests:
```python
pytest
```
