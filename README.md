![GitHub release](https://img.shields.io/github/release/pwesters/watts_vision.svg) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Watts Vision for Home Assistant

These are my first steps in creating an add on for home assistant and learning python. There's a lot left to do, including:
- All the things that aren't default options, like program, stop boost, etc.

I'm learning by doing. Please be kind.

## Requirements
A Watts Vision system Cental unit is required to be able to see the settings remotely. See [Watts Vision Smart Home](https://wattswater.eu/catalog/regulation-and-control/watts-vision-smart-home/) and watch the [guide on youtube (Dutch)](https://www.youtube.com/watch?v=BLNqxkH7Td8).

## HACS

Add https://github.com/pwesters/watts_vision to the custom repositories in HACS. A new repository will be found. Click Download and restart Home Assistant. Go to Settings and then to Devices & Services. Click + Add Integration and search for Watts Vision.

## Manual Installation

Copy the watts_vision folder from custom_components to your custom_components folder of your home assistant instance, go to devices & services and click on '+ add integration'. In the new window search for Watts Vision and click on it. Fill out the form with your credentials for the watts vision smart home system.
