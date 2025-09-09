# ThingsBoardLink

<div align="center">

[![PyPI Downloads](static.pepy.tech/badge/thingsboardlink)](pepy.tech/projects/thingsboardlink)
[![PyPI version](badge.fury.io/py/thingsboardlink.svg)](badge.fury.io/py/thingsboardlink)
[![Python Version](img.shields.io/pypi/pyversions/thingsboardlink.svg)](pypi.org/project/thingsboardlink/)
[![License](img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A high-level IoT platform interaction toolkit designed for Python developers**

*IoT Cloud Platform • Developer-Friendly • Production-Ready*

[Chinese](README-zh_CN.md) | [Documentation](docs/en) | [Examples](#examples)

</div>

---

## 🚀 Why ThingsBoardLink?

ThingsBoardLink is a powerful Python package designed to simplify integration with the ThingsBoard IoT platform. It encapsulates ThingsBoard's REST API, providing object-oriented interfaces that allow developers to easily manage devices, process telemetry data, control alarms, and other core functions.

### ✨ Key Features

| **Feature**                 | **Description**                           | **Benefits**                               | **Documentation**                                                       | **Examples**                                                      |
|-----------------------------|-------------------------------------------|--------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------|
| 🔐 **Auth Management**      | Auto JWT & session handling               | Enhanced security, stateless auth          | [client_doc_en.md](docs/en/client_en.md)                                | [01_connect_and_auth.py](examples/01_connect_and_auth.py)         |
| 📱 **Device Management**    | Full device CRUD & credential ops         | Easy lifecycle & access management         | [device_service_doc_en.md](docs/en/services/device_service_en.md)       | [02_device_management.py](examples/02_device_management.py)       |
| 📊 **Telemetry Data**       | Upload, query & fetch history data        | Efficient time-series data handling        | [telemetry_service_doc_en.md](docs/en/services/telemetry_service_en.md) | [03_telemetry_data.py](examples/03_telemetry_data.py)             |
| ⚙️ **Attribute Management** | Client, server & shared attribute ops     | Flexible metadata, dynamic config          | [attribute_service_doc_en.md](docs/en/services/attribute_service_en.md) | [04_attribute_management.py](examples/04_attribute_management.py) |
| 🚨 **Alarm Management**     | Create, query, acknowledge & clear alarms | Timely response, system reliability        | [alarm_service_doc_en.md](docs/en/services/alarm_service_en.md)         | [05_alarm_management.py](examples/05_alarm_management.py)         |
| 🔄 **RPC Calls**            | One-way & two-way remote procedure calls  | Efficient device-cloud command interaction | [rpc_service_doc_en.md](docs/en/services/rpc_service_en.md)             | [06_rpc_calls.py](examples/06_rpc_calls.py)                       |
| 🔗 **Relation Management**  | Create & manage entity relations          | Build topology, complex logic              | [relation_service_doc_en.md](docs/en/services/relation_service_en.md)   | [07_entity_relations.py](examples/07_entity_relations.py)         |

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install thingsboardlink

# Or install with development dependencies
pip install thingsboardlink[dev]
```

### 30-Second Demo
```python
from thingsboardlink import ThingsBoardClient

# Connect to the corresponding cloud platform
with ThingsBoardClient(
    base_url="http://localhost:8080",
    username="tenant@thingsboard.org",
    password="tenant"
) as client:
    # Device ID
    device_id = "MY_DEVICE_ID"
    
    # Retrieve telemetry data for the corresponding device
    value = client.telemetry_service.get_latest_telemetry(device_id)
    print(value)
```

## 📁 Project Architecture

```
ThingsBoardLink/
├── src/thingsboardlink/
│   ├── services/                   # 🛠️ Service module package
│   │   ├── device_service.py       # Device service module
│   │   ├── telemetry_service.py    # Telemetry service module
│   │   ├── attribute_service.py    # Attribute service module
│   │   ├── alarm_service.py        # Alarm service module
│   │   ├── rpc_service.py          # RPC service module
│   │   └── relation_service.py     # Relation service module
│   │
│   ├── client.py                   # 🖥️ Core client module
│   ├── exceptions.py               # 🔧 Exception handling module
│   └── models.py                   # 🚚 Data model module
│
├── examples/                       # 📚 Usage examples
│   ├── 01_connect_and_auth.py      # Connection and authentication example
│   ├── 02_device_management.py     # Device management example
│   ├── 03_telemetry_data.py        # Telemetry data example
│   ├── 04_attribute_management.py  # Attribute management example
│   ├── 05_alarm_management.py      # Alarm management example
│   ├── 06_rpc_calls.py             # RPC call example
│   └── 07_entity_relations.py      # Relation management example
│
└── docs/                           # 📜 Documentation
    ├── zh                          # Chinese - Documentation
    └── en                          # English - Documentation
```