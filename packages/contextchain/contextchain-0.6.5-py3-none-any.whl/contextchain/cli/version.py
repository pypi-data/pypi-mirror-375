#!/usr/bin/env python3
import click
import json
import os
import yaml
from .main_1 import cli
from .main_1 import update_current_schema
import stat
from pathlib import Path
from datetime import datetime
from contextchain.registry.version_manager import list_versions, rollback_version, VersionManager
from contextchain.registry.schema_loader import load_schema
from contextchain.db.mongo_client import get_mongo_client

@cli.command()
@click.option('--pipeline-id', required=True, help='Pipeline ID')
def new_version(pipeline_id):
    """Create a new schema version based on semantic versioning (local copy only)."""
    click.secho(f"\nCreating New Version for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        if not config_path.exists():
            click.secho(f"✗ Config file {config_path} not found. Please run 'init' first.", fg="red", bold=True)
            return
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        versions = list_versions(client, db_name, pipeline_id)
        
        if not versions:
            click.secho(f"✗ No versions found for {pipeline_id}. Starting with v0.1.0.", fg="red", bold=True)
            latest_version = "v0.0.0"
        else:
            latest_version = max(versions, key=lambda x: [int(i) for i in x['schema_version'].replace('v', '').split('.')])['schema_version']

        click.secho(f"Current version: {latest_version}", fg="bright_blue")
        bump_type = click.prompt(
            click.style("Select version bump:", fg="bright_blue"),
            type=click.Choice(["1", "2", "3"]),
            show_choices=True,
            prompt_suffix="\n1. patch   - Fixes or small changes (e.g. v0.4.3)\n"
                         "2. minor   - Add new task(s) or non-breaking config changes (e.g. v0.5.0)\n"
                         "3. major   - Breaking changes, redesign, removal (e.g. v1.0.0)\n> "
        )
        
        latest_nums = [int(i) for i in latest_version.replace('v', '').split('.')]
        if bump_type == "1":  # patch
            latest_nums[2] += 1
        elif bump_type == "2":  # minor
            latest_nums[1] += 1
            latest_nums[2] = 0
        else:  # major
            latest_nums[0] += 1
            latest_nums[1] = 0
            latest_nums[2] = 0
            breaking_changes = click.prompt(click.style("What breaking changes are you introducing? (description)", fg="bright_blue"), default="")

        new_version = f"v{latest_nums[0]}.{latest_nums[1]}.{latest_nums[2]}"
        
        schema = load_schema(client, db_name, pipeline_id, latest_version)
        if not schema:
            click.secho(f"✗ No schema found for version {latest_version}.", fg="red", bold=True)
            return
        
        schema["schema_version"] = new_version
        schema["created_at"] = datetime.utcnow().isoformat() + "Z"
        schema["created_by"] = os.getenv("USER", "unknown")
        schema["metadata"]["parent_version"] = latest_version
        schema["metadata"]["status"] = "draft"
        schema["metadata"]["changelog"] = [f"Auto-generated new version {new_version}"]
        if bump_type == "3" and breaking_changes:
            schema["metadata"]["changelog"].append(f"Breaking changes: {breaking_changes}")

        schema_dir = Path(f"schemas/{pipeline_id}")
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_path = schema_dir / f"{new_version}.json"
        with schema_path.open("w") as f:
            json.dump(schema, f, indent=2)
        schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        click.secho(f"✓ New schema version {new_version} created locally: {schema_path}", fg="bright_green", bold=True)

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def version_list(pipeline_id):
    """List schema versions for a pipeline."""
    click.secho(f"\nListing Versions for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        versions = list_versions(client, db_name, pipeline_id)
        if not versions:
            click.secho(f"No versions found for {pipeline_id}.", fg="bright_yellow")
            return
        click.secho(f"Found {len(versions)} version(s):", fg="bright_green")
        for v in versions:
            is_latest = " (latest)" if v.get("is_latest", False) else ""
            click.secho(f"  • Version {v['schema_version']}{is_latest}: Created {v['created_at']}", fg="bright_cyan")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', required=True, help='Version to rollback to')
def version_rollback(pipeline_id, version):
    """Rollback to a previous schema version."""
    click.secho(f"\nRolling Back Pipeline {pipeline_id} to Version {version}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        rollback_version(client, db_name, pipeline_id, version)
        click.secho(f"✓ Rolled back {pipeline_id} to version {version}.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, pipeline_id, version)
    except ValueError as e:
        click.secho(f"✗ Rollback error: {e}", fg="red", bold=True)
        return
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return