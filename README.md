# RAPT Cloud Integration for Home Assistant

![hacs_badge](https://img.shields.io/badge/HACS-Custom-blue.svg)

This is a custom integration for Home Assistant that connects to [RAPT Cloud](https://app.rapt.io) and allows you to monitor and control your BrewZilla, RAPT Pill, or other RAPT-compatible brewing devices.

## Features

- Cloud polling for real-time updates from your devices.
- Supports multiple device types including:
  - BrewZilla (temperature, heating, pump, etc.)
  - RAPT Pill (gravity, temperature, battery)
- Displays sensor values such as:
  - Temperature (°C)
  - Specific Gravity (SG)
  - Battery Voltage (V)
  - Target Temperature
  - Heating State
  - Pump State
- Control entities:
  - Heating switch
  - Pump switch
  - Heating Utilization (%)
  - Pump Utilization (%)
  - Target Temperature (°C)

## Installation (via HACS)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Go to **HACS > Integrations**.
3. Click the three dots in the top right and choose **Custom Repositories**.
4. Add this repository: https://github.com/berra200/home-assistant-rapt-cloud and choose **Integration** as category.
5. Find `RAPT Cloud` in the HACS list and install it.
6. Restart Home Assistant.
7. Go to **Settings > Devices & Services** and click **Add Integration**.
8. Search for `RAPT Cloud` and follow the configuration flow.

## Configuration

- You need an **API key** from RAPT Cloud (not just a password) to authenticate.
- The integration automatically discovers your devices linked to your account.

## Upcoming Features

- Additional device types and enhanced sensor/control options.
- Improved error handling and stability.

## Tips & Notes

- The integration polls your devices periodically to provide real-time updates.
- Make sure your API key has the correct permissions in RAPT Cloud.
- Feedback and contributions are welcome via GitHub issues and pull requests.

## License

[MIT](LICENSE)
