# Attendance Device Simulators

Simulates popular punching/attendance machines by sending real HTTP requests to your backend API — no physical devices needed.

## Quick Start

1. **Ensure your Django server is running** on `http://127.0.0.1:8000`:
   ```bash
   cd Backend
   python manage.py runserver
   ```

2. **Register a device**: Run `python manage.py setup_env` in your Backend folder to automatically create the devices in the database.
   You can also set the `SIMULATOR_DEVICE_TOKEN` environment variable to reuse a known device token.

3. **Run a simulator**:

   **Single punch for one employee:**
   ```bash
   python simulators/simulate.py hikvision EMP001
   ```

   **Batch generate historical data (5 days):**
   ```bash
   python simulators/simulate.py zkteco EMP001,EMP002 --batch --days 5
   ```

   **Interactive loop (alternates in/out every 3s):**
   ```bash
   python simulators/simulate.py suprema EMP001 --interactive --delay 3
   ```

   **Run ALL brands at once:**
   ```bash
   python simulators/simulate.py all EMP001,EMP002 --days 10
   ```

   **List available simulators:**
   ```bash
   python simulators/simulate.py list
   ```

## Available Simulators

| Command       | Brand     | Device Type              | Real-World Equivalent     |
|---------------|-----------|--------------------------|---------------------------|
| `hikvision`   | Hikvision | `hikvision_ds-k1t6`      | DS-K1T6 Face Terminal     |
| `zkteco`      | ZKTeco    | `zkteco_k30`             | K30 / MB360 / SpeedFace   |
| `anviz`       | Anviz     | `anviz_vf30`             | VF30 / T5 / CrossChex     |
| `suprema`     | Suprema   | `suprema_biostation2`    | BioStation 2 / FaceStation 2 |
| `dahua`       | Dahua     | `dahua_as7212x`          | DHI-AS7212X Face Terminal |
| `idemia`      | IDEMIA    | `idemia_morphowave`      | MorphoWave / Sigma        |
| `sifarma`     | Sifarma   | `sifarma_biometric`      | Sifarma Biometric Reader  |

## Each Simulator

Every brand simulator:
- Creates or uses a `DeviceConfiguration` entry in your database
- Sends punches via `POST /api/v1/device/push/` with proper `X-Device-Token` auth
- Supports **single**, **batch**, and **interactive** modes
- Prints realistic device metadata (serial, MAC, firmware, IP, etc.)
- Generates realistic attendance patterns (shift-specific, lunch breaks, overtime, weekends)

## Options (all brands)

```
positional arguments:
  employees              Employee ID(s). Comma-separated for multiple.

options:
  --url URL              Backend base URL (default: http://127.0.0.1:8000)
  --token TOKEN          Device API token (UUID). Auto-generated if omitted.
  --device-name NAME     Friendly device name
  -i, --interactive      Interactive loop (alternates in/out every N sec)
  --delay SECONDS        Seconds between punches in interactive mode (default: 3.0)
  -b, --batch            Generate historical batch data
  --days DAYS            Past days to simulate in batch mode (default: 5)
```

## Tips

- **Create employees first** in your app so `external_id` values like `EMP001` exist.
- Use `--url http://your-server:8000` to test against a remote deployment.
- Run `python simulators/simulate.py all EMP001..EMP010 --days 30` for a realistic month of test data.
- Each simulator registers a *new* device token by default. Set `--token` or the env var `SIMULATOR_DEVICE_TOKEN` to reuse one.
