# Period Tracker
**period-tracker** is a lightweight, easy-to-use Python application to track menstrual cycles and analyse cycle statistics.

## Features
- Record period start dates and durations
- Analyse cycle statistics (average length, standard deviation, min, max)
- Data persistence using JSON files
- Secure your data using GPG asymmetric encryption.

## Screenshots
Here’s a few screenshots of the Period Tracker app in action:

![Period Tracker Screenshot](assets/screenshot_01.png)

![Period Tracker Screenshot 2](assets/screenshot_02.png)

## Installation

### Prerequisites
- Python 3.7 or higher
- `pip` + `pipx` installed (recommended for isolated installs)
- `git`
- `gpg` ([GNU Privacy Guard](https://www.gnupg.org/download/)) must be installed and accessible in your system path.

### From PyPi (recommended)
You can install **period-tracker** with `pipx` from the [PyPi](https://pypi.org/project/period-tracker/) repo.
```sh
pipx install period-tracker
```

### From source
Clone the repository and install:
```sh
git clone https://codeberg.org/kingorgg/period_tracker.git
cd period_tracker
pipx install .
```

## Usage
After installation, launch the tracker using the command:
```sh
period-tracker
```
## (OPTIONAL) create a shortcut
Copy the following content (replace `USERNAME` with your actual username) to a new file at:
```sh
$HOME/.local/share/applications/period-tracker.desktop
```

```ini
[Desktop Entry]
Name=Period Tracker
GenericName=Period Tracker
Exec=/home/USERNAME/.local/bin/period-tracker
Terminal=false
Type=Application
Categories=Other;
```

## Uninstallation
To uninstall the package installed via pipx:
```sh
pipx uninstall period-tracker
```

## Data Encryption
Period Tracker uses **GPG asymmetric encryption** to protect your data.

### How it works
The app encrypts your data file (`data.json`) using your **GPG public key**. Only your corresponding **private key** can decrypt it.

### Requirements
Make sure you have a GPG key pair generated (using `gpg --gen-key`). When you first load the period-tracker, you'll be prompted to enter your email address or key ID/fingerprint.

You can check what keys you have by running:
```cli
gpg --list-keys
```

## Data Storage
Data is stored locally and encrypted with gpg in:
```cli
$XDG_DATA_HOME/period-tracker/data.json.gpg # Linux

C:\Users\USERNAME\AppData\Local\period-tracker\data.json.gpg # Windows
```

## Config
Your config file is located in:
```cli
$XDG_CONFIG_HOME/period-tracker/config.json # Linux

C:\Users\USERNAME\AppData\period-tracker\config.json # Windows
```

## Development
For development, install optional dependencies:
```sh
pip install .[dev]
```
Run tests with:
```sh
pytest tests/
```

## License
This project is licensed under the [MIT License](https://codeberg.org/kingorgg/period_tracker/raw/branch/main/LICENSE).
