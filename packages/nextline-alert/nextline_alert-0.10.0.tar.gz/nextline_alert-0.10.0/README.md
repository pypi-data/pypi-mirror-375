# nextline-alert

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-alert.svg)](https://pypi.org/project/nextline-alert)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-alert.svg)](https://pypi.org/project/nextline-alert)

[![Test Status](https://github.com/simonsobs/nextline-alert/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-alert/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-alert/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-alert/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-alert/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-alert)

A plugin for [nextline-graphql](https://github.com/simonsobs/nextline-graphql).
Emit alerts to [Campana](https://github.com/simonsobs/campana)

## Installation

```console
pip install nextline-alert
```

## Alert types

- **Run failed:** The script execution by `nextline` ended with an uncaught
  exception except for `KeyboardInterrupt`.
- **Idle:** The time specified by `NEXTLINE_ALERT__IDLE_TIMEOUT_MINUTES`
  minutes has passed without the script execution since the last run ended or
  the backend started.

## Configuration

| Environment variable                   | Default value             | Description                 |
| -------------------------------------- | ------------------------- | --------------------------- |
| `NEXTLINE_ALERT__CAMPANA_URL`          | `http://httpbin.org/post` | The CAMPANA endpoint        |
| `NEXTLINE_ALERT__PLATFORM`             | `localhost`               | The platform name           |
| `NEXTLINE_ALERT__IDLE_TIMEOUT_MINUTES` | 20.0                      | The idle timeout in minutes |
