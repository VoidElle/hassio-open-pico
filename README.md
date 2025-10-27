<div align="center">
  <img src="./assets/logo.png" alt="Logo" height="200">
  <br>
  <small><em>(Official Tecnosystemi logo not used due to copyright restrictions)</em></small>
  <br><br>
  <h1>🏠 Hassio Open Pico</h1>
  <p><em>Home Assistant integration for Tecnosystemi Pico devices</em></p>
</div>


Hassio Open Pico is a Home Assistant integration that enables management of Pico devices (manufactured by Tecnosystemi) through Home Assistant.

This integration provides monitoring, control, and automation capabilities for Pico devices, offering an intuitive interface for Home Assistant users.

This integration took inspiration from:
- The official [Tecnosystemi](https://play.google.com/store/apps/details?id=it.tecnosystemi.TS&hl=it) mobile application
- My own reverse engineered POC mobile application [Open Pico](https://github.com/VoidElle/open-pico-app)

## Installation 📦
### Via HACS (Recommended) ⭐
[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=VoidElle&repository=hassio-open-pico&category=integration)

### Via HACS (Manual)
1. Add custom repository:
   - Open HACS in your Home Assistant interface
    - Go to "Integrations" tab
    - Click on the three dots in the top right corner and select "Custom repositories"
    - Enter the repository URL: `https://github.com/VoidElle/hassio-open-pico`
    - Select "Integration" as the category
    - Click "Add"


2. Install the integration:
   - In HACS Integrations, click + Explore & Download Repositories
   - Search for "Hassio Open Pico"
   - Click on the integration and then Download
   - Select the latest version and click Download


3. Restart Home Assistant 🔄

### Manual Installation 🔧
1. Copy the repository content inside a folder called `hassio_open_pico`
2. Move the folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration ⚙️
1. Go to Settings > Devices & Services
2. Click "Add Integration" and search for "Hassio Open Pico"
3. Enter your Tecnosystemi account credentials
4. Enter the PIN common to all devices

## Limitations ⚠️
- Support only for Pico devices
- Single user support only (APIs support only one valid token at a time)
- No support for plant differentiation - all devices are exposed at the same level; use Home Assistant areas for organization
- 🚨 PIN must be the same across all Pico devices 🚨

## Tested On 🧪
- PICO PRO PLUS 30 **(ACD100052)**

*Most features should work on all Pico models*

## Contributing 🤝

Contributions are welcome! 

### How to Help
- 🐛 **Report bugs** via [GitHub Issues](https://github.com/VoidElle/hassio-open-pico/issues)
- 🌍 **Translate** to more languages
- 🔧 **Submit PRs** for improvements via [GitHub Pull requests](https://github.com/VoidElle/hassio-open-pico/pulls)
- 📖 **Improve documentation**

### Development
1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/name`
3. Follow [Home Assistant dev guidelines](https://developers.home-assistant.io/)
4. Submit a PR with clear description


## Work in Progress 🚧
- [ ] Custom error messages
- [ ] Multi-language support (currently Italian and English only)
