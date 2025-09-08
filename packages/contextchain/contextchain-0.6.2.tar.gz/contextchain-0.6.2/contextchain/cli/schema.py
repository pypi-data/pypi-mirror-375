#!/usr/bin/env python3
import click
import json
import os
import sys
from pathlib import Path
import yaml
from .main_1 import cli
from .main_1 import update_current_schema, copy_schema_file
from contextchain.engine.validator import validate_schema
from contextchain.registry.version_manager import push_schema
from contextchain.registry.schema_loader import load_schema
from contextchain.db.mongo_client import get_mongo_client

@cli.command()
@click.option('--file', type=click.Path(exists=True), required=True, help='Path to schema file')
def schema_compile(file):
    """Validate a schema file."""
    click.secho("\nValidating Schema...", fg="bright_yellow", bold=True)
    try:
        with open(file, 'r') as f:
            schema = json.load(f)
        validate_schema(schema)
        click.secho("✓ Schema validated successfully.", fg="bright_green", bold=True)
    except ValueError as e:
        click.secho(f"✗ Validation error: {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--file', type=click.Path(exists=True), required=True, help='Path to schema file')
def schema_push(file):
    """Push a schema to MongoDB with versioning."""
    click.secho("\nPushing Schema to MongoDB...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        with open(file, 'r') as f:
            schema = json.load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        validate_schema(schema)
        push_schema(client, db_name, schema)
        click.secho(f"✓ Schema {schema['pipeline_id']} pushed to MongoDB with version {schema['schema_version']}.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, schema["pipeline_id"])
        copy_schema_file(schema["pipeline_id"], schema["metadata"].get("parent_version", "v0.0.0"), schema["schema_version"])
    except ValueError as e:
        click.secho(f"✗ Validation error: {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Push error: {e}", fg="red", bold=True)
        sys.exit(1)