# RAPT Cloud Integration for Home Assistant

![hacs_badge](https://img.shields.io/badge/HACS-Custom-blue.svg)

This is a custom integration for Home Assistant that connects to [RAPT Cloud](https://app.rapt.io) and allows you to monitor and control your BrewZilla or other RAPT-compatible brewing devices.

## Features

- Cloud polling for real-time updates from your BrewZilla.
- Displays sensor values such as:
  - Temperature
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
4. Add this repository: https://github.com/berra200/home-assistant-rapt-cloud Choose **Integration** as category.
5. Find `RAPT Cloud` in the HACS list and install it.
6. Restart Home Assistant.
7. Go to **Settings > Devices & Services** and click **Add Integration**.
8. Search for `RAPT Cloud` and follow the configuration flow.

## Configuration

You will need your RAPT Cloud credentials (email and password) to authenticate. The integration will automatically discover your BrewZilla devices associated with your account.

## Known Limitations

- Heating Utilization value may reset to 0 in the API after setting it via the RAPT web portal (API bug).
- Only BrewZilla is currently supported. Support for Pill and other devices may be added later.

## License

[MIT](LICENSE)
