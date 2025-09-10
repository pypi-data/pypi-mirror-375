# Mixtrain

**Mixtrain** is a Python SDK and CLI for [mixtrain.ai](https://mixtrain.ai) platform.

## Installation

Using uv
```bash
uv add mixtrain
```
or if you use pip

```bash
pip install mixtrain
```

To install mixtrain CLI globally, using uv

```bash
uv tool install mixtrain
```
or if you use pipx

```bash
pipx mixtrain
```

## Quick Start

### Authentication

First, authenticate with the Mixtrain platform:

```bash
mixtrain login
```

### CLI Usage

Refer to `mixtrain --help` for the full list of commands.

### Python SDK

#### Basic Dataset Operations

```python
import mixtrain.client as mix

# Create a dataset from file
mix.create_dataset_from_file("my_dataset", "data.csv", description="My dataset")

# List datasets
datasets = mix.list_datasets()
print(datasets)

# Get direct access to remote dataset
table = mix.get_dataset("my_dataset")

# Scan table data
scan = table.scan(limit=1000)
df = scan.to_polars()  # or .to_pandas() or .to_duckdb("my_dataset")
print(df.head())

```
