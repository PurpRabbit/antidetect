# Antidetect Browser

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description

This script allows you to create and manage multiple profiles and proxies. It provides functionality to create and configure profiles with various options, as well as create and manage proxies for use with the profiles. The script provides commands to list profiles and proxies, start and stop profiles, change profile settings, and more.

## Installation

    git clone https://github.com/PurpRabbit/antidetect

### Prerequisites

- Installed chrome browser required

### Getting Started

1. Create new folder and navigate to it.
2. Clone the repository.
3. Install required dependencies.

## Usage

    python antidetect.py

![Script start message](https://imgur.com/a/GFYzJOx)

## Tables displayed information

![Profiles table](https://imgur.com/a/boHwTa0)

    ID - profile id.
    Name - profile name.
    Active - is profile running.
    Proxy - proxy ID, related to proxies table.
    Description - profile description.

![Proxies table](https://imgur.com/a/QWeundI)

    ID - proxy id.
    Country - proxy country.
    Address - proxy ipv4 address.
    Port - proxy port.
    Username - proxy auth username.
    Password - proxy auth password.
    Valid - proxy validation (None - proxy validation was not executed, False - proxy invalid, True - proxy is valid).
    Profiles count - count of profiles that are using this proxy.

## License

This script is licensed under the [MIT License](LICENSE).