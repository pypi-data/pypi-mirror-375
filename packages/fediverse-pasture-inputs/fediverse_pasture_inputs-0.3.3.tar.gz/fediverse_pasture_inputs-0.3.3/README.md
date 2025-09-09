<!--
SPDX-FileCopyrightText: 2024 Helge

SPDX-License-Identifier: MIT
-->

# fediverse-pasture-inputs

Versioned inputs to generate Fediverse software interoperability data.

These inputs are used to populate the funfedi.dev [Support Tables](https://funfedi.dev/support_tables/).

## Development

```bash
poetry build --format wheel
```

will allow you to build a wheel file for the project. By
placing this in the work directory of [interoperability-data](https://codeberg.org/funfedidev/interoperability-data)
and then running pip install with it

```bash
pip install ./fediverse_pasture_inputs-*-py3-none-any.whl
```

one can run the tests against a new input.

## Assets

The assets in `assets` should be served under `http://pasture_one_actor/assets`
for some tests to work. These are available as a zip file [here](https://inputs.funfedi.dev/assets/fediverse_pasture_assets.zip).

## Funding

This code was created as part of [Fediverse Test Framework](https://nlnet.nl/project/FediverseTestFramework/).

A project funded through the [NGI0 Core](https://nlnet.nl/core) Fund,
a fund established by [NLnet](https://nlnet.nl/) with financial support from
the European Commission's [Next Generation Internet](https://ngi.eu/) programme,
under the aegis of DG Communications Networks, Content and Technology
under grant agreement No 101092990.
