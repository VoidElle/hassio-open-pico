<div align="center">
  <img src="./assets/logo.png" alt="Logo" height="200">
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
1. Copy the `custom_components/hassio_open_pico` folder to your `custom_components` directory
2. Restart Home Assistant

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
- PICO PRO 30 **(ACD100056)**

*Should work on all Pico models*

## Token Architecture 🔐

The most complex aspect of this integration is obtaining and maintaining valid API access tokens. The token mechanism has been **completely reverse-engineered from the official Tecnosystemi mobile application** through extensive analysis of network traffic and binary decompilation.

### Technical Implementation

Unlike conventional stateless bearer tokens, Pico's authentication system employs a sophisticated **stateful token architecture** where the client bears responsibility for token lifecycle management:

- **Token Structure**: Each token encapsulates encrypted payload in the format `{session_identifier}_{call_counter}`
- **Cryptographic Scheme**: AES-256 encryption using CBC mode with PKCS7 padding, base64-encoded output
- **Key Derivation**: Composite key generated from fixed device identifier (first 8 characters) + static salt, hashed with SHA-256 and truncated to 32 bytes
- **Counter Mechanism**: Every API request requires decrypting the token, incrementing the embedded counter, and re-encrypting before transmission

### Security Implications

- **Mutual Exclusion**: Token invalidation occurs upon any successful authentication event (integration login, mobile app login, or direct API access), enforcing single-session semantics
- **Replay Protection**: The incrementing counter prevents replay attacks and ensures request ordering
- **Zero IV**: Uses a null initialization vector (16 zero bytes) for deterministic encryption

This architecture, while unconventional, provides robust session management at the cost of concurrent access limitations. The reverse-engineered implementation maintains full compatibility with the original mobile application's cryptographic protocols.

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