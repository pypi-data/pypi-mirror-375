
# pytractive

**Unofficial** asynchronous Python client for the [Tractive](https://tractive.com) REST API.

- This project and its author are not affiliated with Tractive GmbH.
- You must have an active Tractive subscription to use Tractive devices and their service.
- Tractive may change their API at any time; this client may stop working. Please open an issue if something breaks.



### Requirements
- Python 3.13
- Active Tractive account (username and password)

### Installation
- From PyPI:
```bash
pip install pytractive
```

- From source:
```bash
git clone https://forge.wolfhound.dev/wolfhound/pytractive.git
cd pytractive
pip install -e .
```

### Quickstart (🚧)

- This logs in, lists trackers and pets, and prints a few fields:

```python
import asyncio
from pytractive import Tractive

async def main():
    async with Tractive("example@example.com", "Super-Secret-Password") as client:
        devices = await client.trackers()
        for device in devices:
            data = await device.details()
            print(
                f"Device ID: {data['_id']}, Model: {data['model_number']}, Battery State: {data['battery_state']}"
            )

            data = await device.hw_info()
            print(f"  Battery Level: {data['battery_level']}%")

            data = await device.pos_report()
            print(f"  Last Position: {data['latlong']}, Altitude: {data['altitude']} m")

            data = await device.positions(1757347200, 1757350800, "json")
            for pos in data[:3]:
                print(
                    f"    Time: {pos['time']}, Position: {pos['latlong']}, Altitude: {pos['alt']} m, Speed: {pos['speed']} m/s"
                )

        await asyncio.sleep(5)
        pets = await client.trackable_objects()
        for pet in pets:
            data = await pet.details()
            print(
                f"Pet ID: {data['_id']}, Name: {data['details']['name']}, Type: {data['details']['pet_type']}"
            )

if __name__ == "__main__":
    asyncio.run(main())
```


Authentication & session behavior
- The client authenticates using the Tractive account username and password.
- Provide credentials when constructing the client: ```Tractive(username, password)```.
- The client stores the login in the client instance and will renew the session only if it expires.
- The client is usable as an async context manager (```async with ...```) which handles opening and closing the session automatically.

API reference (high level)
- Construction:
  - ```Tractive(username: str, password: str)```
- Common client calls:
  - ```await client.trackers()``` → list of tracker device objects
  - ```await client.trackable_objects()``` → list of pets/trackable objects
  - ```await client.bulk_send(list_of_requests)``` → graph-like bulk request (see example below)
- Device object methods:
  - ```await device.details()```
  - ```await device.hw_info()```
  - ```await device.pos_report()```
  - ```await device.positions(start_ts, end_ts, format)```
- Pet object methods:
  - ```await pet.details()```

bulk_send example
```python
response = await client.bulk_send(
    [
        {"_id": "AXJSHQVY", "_type": "tracker"},
        {"_id": "68bf8adc9170ca50e1b5fbc4", "_type": "user_setting"},
        {"_id": "68bf8ae0371900fe8a6c7308", "_type": "pet"},
        {"_id": "68bf8ae8658beb6088ec4076", "_type": "subscription"},
        {"_id": "68bf8aec8b82e9b0749a3da7", "_type": "user_demographic"},
        {"_id": "8mWQGvPB7ZVwf2djvLduu", "_type": "image"},
        {"_id": "68bf8af1a239eb840c853f65", "_type": "user_detail"},
    ]
)
```
- The ```bulk_send``` endpoint is more graph-like and will be documented further later.


### Development
- Clone repository:
```bash
git clone https://forge.wolfhound.dev/wolfhound/pytractive.git
cd pytractive
```
- Project management uses ```uv```. See: https://docs.astral.sh/uv/getting-started/installation/#installing-uv
- Common commands:
  - Bump version:
    ```bash
    uv version --bump {patch,minor,major}
    ```
  - Build:
    ```bash
    uv build
    ```
- Tests:
  - Currently there are no tests.

### Contributing
- Fork the repo, create a feature branch, run tests/lints locally, and open a PR.

### Acknowledgements
This project started as a fork of [zhulik/aiotractive](https://github.com/zhulik/aiotractive).
<br>Thanks to the open-source community.

