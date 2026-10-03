# Passport Specification v1

## Required fields

### `passport`
Contains the Passport specification version.

### `agent`
- `id`
- `name`
- `version`
- `description`

### `identity`
- `capabilities`

### `behavior`
- `input.type`
- `output.type`

### `tools`
Each tool may declare:
- `name`
- `description`
- `input_schema`
- `output_type`

### `model`
- `interface_version`
- `provider`
- `model`

`provider: any` and `model: any` mean that the portable contract does not
require a particular provider/model.

### `runtime`
- `api_version`
- `compatible`

### `verification`
Lists verification categories required by the Passport.

## Fingerprint

The normalized Passport representation is serialized deterministically and
hashed with SHA-256.

The fingerprint identifies the Passport contents. It is not a digital
signature and does not by itself prove who issued a Passport.
