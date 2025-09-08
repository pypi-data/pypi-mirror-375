#!/usr/bin/env python3
import click
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
import subprocess
import os
import stat
import logging
from contextchain.engine.validator import validate_schema
from contextchain.engine.executor import execute_pipeline, execute_single_task
from contextchain.registry.version_manager import push_schema, list_versions, rollback_version, VersionManager
from contextchain.registry.schema_loader import load_schema
from contextchain.db.mongo_client import get_mongo_client
from contextchain.db.collections import setup_collections
from dotenv import load_dotenv
import time
import shutil

# Load environment variables from .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Load colorama for better color support
try:
    import colorama
    colorama.init()
except ImportError:
    pass

def show_banner():
    """Display the CLI banner with ASCII art and colors."""
    ascii_art = r"""
 ██████╗ ██████╗ ███╗   ██╗████████╗███████╗██╗  ██╗████████╗
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝
██║     ██║   ██║██╔██╗ ██║   ██║   █████╗   ╚███╔╝    ██║   
██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝   ██╔██╗    ██║   
╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██╔╝ ██╗   ██║   
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   
                                                              
 ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
██╔════╝██║  ██║██╔══██╗██║████╗  ██║
██║     ███████║███████║██║██╔██╗ ██║
██║     ██╔══██║██╔══██║██║██║╚██╗██║
╚██████╗██║  ██║██║  ██║██║██║ ╚████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
    """
    click.secho("=" * 60, fg="bright_blue", bold=True)
    click.secho(ascii_art, fg="bright_blue", bold=True)
    click.secho("         ContextChain v1.0 CLI", fg="bright_cyan", bold=True)
    click.secho("         Orchestrate AI and Full-Stack Workflows", fg="bright_cyan", bold=True)
    click.secho("                        v1.0", fg="bright_white", bold=True)
    click.secho("=" * 60, fg="bright_blue", bold=True)

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
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "schema": schema
        }
        try:
            if not current_schema_path.exists():
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
                current_schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            elif os.access(current_schema_path, os.W_OK):
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
                current_schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            else:
                click.secho(f"✗ current_schema.json for {pipeline_id} is read-only. Attempting to fix permissions...", fg="yellow", bold=True)
                os.chmod(current_schema_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                with current_schema_path.open("w") as f:
                    json.dump(meta, f, indent=2)
        except PermissionError:
            click.secho(f"✗ Failed to update current_schema.json for {pipeline_id} due to permissions. Please run 'chmod u+w {current_schema_path}' manually.", fg="red", bold=True)
            return
        click.secho(f"✓ Updated current_schema.json for {pipeline_id} (version: {schema.get('schema_version', 'v0.0.0')})", fg="bright_green", bold=True)
    else:
        click.secho(f"✗ No schema found for {pipeline_id}", fg="red", bold=True)

def copy_schema_file(pipeline_id, old_version, new_version):
    """Create a backup copy of the schema file with a timestamp suffix without overwriting the original."""
    source_path = Path(f"schemas/{pipeline_id}/{new_version}.json")
    if source_path.exists():
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = source_path.with_name(f"{source_path.stem}.{timestamp}{source_path.suffix}")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, backup_path)
        backup_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        click.secho(f"✓ Created backup schema: {backup_path} (version: {new_version})", fg="bright_green", bold=True)
    else:
        click.secho(f"✗ Source file {source_path} not found for backup.", fg="red", bold=True)

class ColoredGroup(click.Group):
    """Custom Click Group that shows banner and colored help."""
    def format_help(self, ctx, formatter):
        show_banner()
        click.secho("\nUsage: contextchain [OPTIONS] COMMAND [ARGS]...", fg="bright_white", bold=True)
        click.secho("\nContextChain v1.0 CLI", fg="bright_cyan")

        click.secho("\nOptions:", fg="bright_yellow", bold=True)
        click.secho("  -h, --help      Show this help message and exit.", fg="bright_cyan")

        click.secho("\nCommands (grouped by category):", fg="bright_yellow", bold=True)

        click.secho("\n  Initialization:", fg="bright_green", bold=True)
        click.secho("    init          Initialize a new pipeline with a JSON schema and MongoDB setup.", fg="bright_cyan")
        click.secho("    new-version   Create a new schema version based on semantic versioning (local copy only).", fg="bright_cyan")

        click.secho("\n  Schema Management:", fg="bright_green", bold=True)
        click.secho("    schema-compile  Validate a schema file.", fg="bright_cyan")
        click.secho("    schema-push     Push a schema to MongoDB with versioning.", fg="bright_cyan")
        click.secho("    schema-pull     Pull a schema from MongoDB.", fg="bright_cyan")
        click.secho("    schema-current  Display the current schema version.", fg="bright_cyan")
        click.secho("    version-list    List schema versions for a pipeline.", fg="bright_cyan")
        click.secho("    version-rollback  Rollback to a previous schema version.", fg="bright_cyan")

        click.secho("\n  Execution:", fg="bright_green", bold=True)
        click.secho("    run            Run an entire pipeline.", fg="bright_cyan")
        click.secho("    run-task       Run a single task for development.", fg="bright_cyan")

        click.secho("\n  Collaboration:", fg="bright_green", bold=True)
        click.secho("    ccshare-init    Initialize a .ccshare file for collaborative MongoDB Atlas access.", fg="bright_cyan")
        click.secho("    ccshare-join    Join an existing .ccshare collaboration.", fg="bright_cyan")
        click.secho("    ccshare-status  Check the status of the .ccshare configuration.", fg="bright_cyan")

        click.secho("\n  Utilities:", fg="bright_green", bold=True)
        click.secho("    list-pipelines  List all pipelines in MongoDB.", fg="bright_cyan")
        click.secho("    logs            Display logs for a pipeline.", fg="bright_cyan")
        click.secho("    results         Display results for a specific task.", fg="bright_cyan")

        click.secho("\nNotes:", fg="bright_yellow", bold=True)
        click.secho("  - Use 'contextchain COMMAND --help' for detailed options of each command.", fg="bright_cyan")

# Define cli as a click.Group instance at the top level
cli = click.group(cls=ColoredGroup, context_settings={"help_option_names": ["-h", "--help"]})

if __name__ == "__main__":
    cli()