# Watts Vision for Home Assistant

These are my first steps in creating an add on for home assistant and learning python. There's a lot left to do, including:
- Set the mode of the thermostat
- All the things that aren't default options, like program, stop boost, etc.

I'm learning by doing. Please be kind.

## Requirements
A Watts Vision system Cental unit is required to be able to see the settings remotely. See [Watts Vision Smart Home](https://wattswater.eu/catalog/regulation-and-control/watts-vision-smart-home/) and watch the [guide on youtube (Dutch)](https://www.youtube.com/watch?v=BLNqxkH7Td8).

## Installation

Copy the watts_vision folder from custom_components to your custom_components folder of your home assistant instance.

Add the following lines to configuration.yaml

```yaml
watts_vision:
  username: [username]
  password: [password]
```
