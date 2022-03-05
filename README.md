# uhabits_converter
[![Build Status](https://github.com/ConorSheehan1/uhabits_converter/workflows/ci/badge.svg)](https://github.com/ConorSheehan1/uhabits_converter/actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tested Operating Systems](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/ConorSheehan1/uhabits_converter/main/.github/workflows/ci.yml&label=os&query=$.jobs.build.strategy.matrix.os)](https://github.com/ConorSheehan1/uhabits_converter/blob/main/.github/workflows/ci.yml#L25)
[![Tested python versions](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/ConorSheehan1/uhabits_converter/main/.github/workflows/ci.yml&label=Tested%20python%20versions&query=$.jobs.build.strategy.matrix.python)](https://github.com/ConorSheehan1/uhabits_converter/blob/main/.github/workflows/ci.yml#L26)

[Loop Habit / uhabits](https://github.com/iSoron/uhabits) converter.

## Warnings
Please back up your data! By default this project does copy your data to a new db before editing it, but I make no promises it won't break on write or import.

This project is developed in my spare time, so it could be out of sync with [Loop Habit / uHabits](https://github.com/iSoron/uhabits).
It has been tested with version [2.0.3](https://github.com/iSoron/uhabits/releases/tag/v2.0.3).


## Features
1. Convert boolean habits to the new numeric habit type.

## Installation
```bash
# install python
pip install poetry
poetry install
```

### Steps to convert habits
1. Follow the instructions for **How can I export a full backup of my data?**
    1. https://github.com/iSoron/uhabits/discussions/689 
    > Select the option "Export full backup" on the settings screen.
2. Copy the .db file to your computer
3. run `poetry run task cli`
    1. You can specify arguments up front or interactively. e.g.
    `poetry run task cli --db=Loop_Habits_Backup_2022-02-28_220305.db --habits=Gym,Coffee`
    this will convert the habits Gym and Coffee from boolean to numeric habits.
    now you can track hours in the gym and cups of coffee, rather than just the days you went to the Gym or drank coffee.
4. copy the `output.db` file back to your android device.
5. follow the instructions for **How can I restore a full backup?**
    > First, go to the settings screen and tap "Import data". A file browser should appear. Tap the menu icon (the one with three vertical lines) and select the app where your backup is stored, such as Google Drive.

    > If your backup file is located in your SD card, after tapping "Import data", tap the icon with three dots on the top right corner of the screen and select "Show internal storage". Then, tap the menu icon (the one with three vertical lines) and select your SD card.


### Development
See [DEV.md](./DEV.md)