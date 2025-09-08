#!/usr/bin/env python3
import click
import json
import os
import sys
from pathlib import Path
from .main_1 import cli  # Import the main cli group
from datetime import datetime
import logging
from contextchain.engine.validator import validate_schema
from contextchain.registry.version_manager import push_schema
from contextchain.registry.schema_loader import load_schema
from contextchain.db.mongo_client import get_mongo_client
import yaml
import shutil

logging.basicConfig(level=logging.INFO)

def update_current_schema(client, db_name, pipeline_id, version=None):
    """Update the current_schema.json with the latest or specified schema version."""
    schema = load_schema(client, db_name, pipeline_id, version)
    if schema:
        schema_dir = Path(f"schemas/{pipeline_id}")
        schema_dir.mkdir(parents=True, exist_ok=True)
        current_schema_path = schema_dir / "current_schema.json"
        meta = {
            "_meta": {
                "pipeline_id": pipeline_id,
                "version": schema.get("schema_version", "v0.0.0"),
                "timestamp": schema.get("created_at", "N/A")
            },
            "schema": schema
        }
        try:
            if not current_schema_path.exists():
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
                current_schema_path.chmod(0o644)
            elif os.access(current_schema_path, os.W_OK):
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
                current_schema_path.chmod(0o644)
            else:
                os.chmod(current_schema_path, 0o644)
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
        except PermissionError:
            click.secho(f"✗ Failed to update current_schema.json for {pipeline_id} due to permissions.", fg="red", bold=True)
            return
        click.secho(f"✓ Updated current_schema.json for {pipeline_id} (version: {schema.get('schema_version', 'v0.0.0')})", fg="bright_green", bold=True)
    else:
        click.secho(f"✗ No schema found for {pipeline_id}", fg="red", bold=True)

def copy_schema_file(pipeline_id, old_version, new_version):
    """Create a backup copy of the schema file with a timestamp suffix."""
    source_path = Path(f"schemas/{pipeline_id}/{new_version}.json")
    if source_path.exists():
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = source_path.with_name(f"{source_path.stem}.{timestamp}{source_path.suffix}")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, backup_path)
        backup_path.chmod(0o644)
        click.secho(f"✓ Created backup schema: {backup_path} (version: {new_version})", fg="bright_green", bold=True)
    else:
        click.secho(f"✗ Source file {source_path} not found for backup.", fg="red", bold=True)

# Define a schema subgroup and add it to the main cli
@cli.group()
def schema():
    """Commands for managing schemas."""
    pass

@schema.command()
@click.option('--file', type=click.Path(exists=True), required=True, help='Path to schema file')
def compile(file):
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

@schema.command()
@click.option('--file', type=click.Path(exists=True), required=True, help='Path to schema file')
def push(file):
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

@schema.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', help='Schema version (default: latest)')
def pull(pipeline_id, version):
    """Pull a schema from MongoDB."""
    click.secho(f"\nPulling Schema for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if schema:
            schema_dir = Path(f"schemas/{pipeline_id}")
            schema_dir.mkdir(parents=True, exist_ok=True)
            schema_path = schema_dir / f"{pipeline_id}.json"
            with schema_path.open("w") as f:
                json.dump(schema, f, indent=2)
            click.secho(f"✓ Schema pulled: {schema_path}", fg="bright_green", bold=True)
        else:
            click.secho(f"✗ Schema {pipeline_id} not found.", fg="red", bold=True)
            return
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@schema.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def current(pipeline_id):
    """Display the current schema version."""
    click.secho(f"\nDisplaying Current Schema for {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id)
        if schema:
            click.secho(f"Current Schema Version: {schema.get('schema_version', 'v0.0.0')}", fg="bright_green", bold=True)
            click.secho(json.dumps(schema, indent=2), fg="bright_cyan")
        else:
            click.secho(f"✗ No schema found for {pipeline_id}", fg="red", bold=True)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return