<div align="center">

# tap-checkly

<div>
  <a href="https://results.pre-commit.ci/latest/github/reservoir-data/tap-checkly/main">
    <img alt="pre-commit.ci status" src="https://results.pre-commit.ci/badge/github/reservoir-data/tap-checkly/main.svg"/>
  </a>
  <a href="https://github.com/reservoir-data/tap-checkly/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/reservoir-data/tap-checkly"/>
  </a>
  <a href="https://github.com/reservoir-data/tap-checkly/">
    <img alt="License" src="https://img.shields.io/pypi/pyversions/tap-checkly"/>
  </a>
</div>

Singer Tap for [Checkly](https://www.checklyhq.com/). Built with the [Meltano Singer SDK](https://sdk.meltano.com).

</div>

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| account_id          | True     | None    | Checkly Account ID |
| token               | True     | None    | API Token for Checkly |
| start_date          | False    | None    | Earliest datetime to get data from |
| include_paid_streams| False    |       0 | Include streams that require a paid Checkly plan |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `tap-checkly --about`

## API Coverage

| API Endpoint                  | Supported | Notes                     |
| :---------------------------- | :-------: | :------------------------ |
| `/v1/alert-channels`          |    ✅     |                            |
| `/v1/alert-notifications`     |    ✅     |  Payment required          |
| `/v1/checks`                  |    ✅     |                            |
| `/v1/check-alerts`            |    ✅     |                            |
| `/v1/check-groups`            |    ✅     |                            |
| `/v1/check-results/{checkId}` |    N/A    | [Heavily rate-limited][1] |
| `/v1/dashboards`              |    ✅     |                            |
| `/v1/locations`               |    ✅     |                            |
| `/v1/maintenance-windows`     |    ✅     |                            |
| `/v1/private-locations`       |    ✅     |                            |
| `/v1/runtimes`                |    ✅     |                            |
| `/v1/snippets`                |    ✅     |                            |
| `/v1/variables`               |    ✅     |                            |

A full list of supported settings and capabilities is available by running: `tap-checkly --about`

### Source Authentication and Authorization

## Usage

You can easily run `tap-checkly` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-checkly --version
tap-checkly --help
tap-checkly --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install hatch
```

### Create and Run Tests

Run integration tests:

```bash
hatch run test:integration
```

You can also test the `tap-checkly` CLI interface directly:

```bash
hatch run sync:console -- --about --format=json
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Go ahead and [install Meltano](https://docs.meltano.com/getting-started/installation/) if you haven't already.

1. Install all plugins

   ```bash
   meltano install
   ```

1. Check that the extractor is working properly

   ```bash
   meltano invoke tap-checkly --version
   ```

1. Execute an ELT pipeline

   ```bash
   meltano run tap-checkly target-jsonl
   ```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to develop your own taps and targets.

[1]: https://developers.checklyhq.com/reference/getv1checkresultscheckid
