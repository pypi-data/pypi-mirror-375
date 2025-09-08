#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from main_1 import cli
import sys
from contextchain.engine.executor import execute_pipeline, execute_single_task
from contextchain.db.mongo_client import get_mongo_client
from contextchain.registry.schema_loader import load_schema

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', help='Schema version (default: latest)')
def run(pipeline_id, version):
    """Run an entire pipeline."""
    click.secho(f"\nRunning Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if not schema:
            click.secho(f"✗ Pipeline {pipeline_id} not found.", fg="red", bold=True)
            sys.exit(1)
        execute_pipeline(client, db_name, schema)
        click.secho(f"✓ Pipeline {pipeline_id} executed successfully.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Execution error: {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--task_id', type=int, required=True, help='Task ID')
@click.option('--version', help='Schema version (default: latest)')
def run_task(pipeline_id, task_id, version):
    """Run a single task for development."""
    click.secho(f"\nRunning Task {task_id} in Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if not schema:
            click.secho(f"✗ Pipeline {pipeline_id} not found.", fg="red", bold=True)
            sys.exit(1)
        task = next((t for t in schema["tasks"] if t["task_id"] == task_id), None)
        if not task:
            click.secho(f"✗ Task {task_id} not found.", fg="red", bold=True)
            sys.exit(1)
        execute_single_task(client, db_name, schema, task)
        click.secho(f"✓ Task {task_id} executed successfully.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Execution error: {e}", fg="red", bold=True)
        sys.exit(1)