#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from contextchain.db.mongo_client import get_mongo_client
from main import cli

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def logs(pipeline_id):
    """Display logs for a pipeline."""
    click.secho(f"\nDisplaying Logs for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        logs = list(client[db_name]["trigger_logs"].find({"pipeline_id": pipeline_id}))
        if logs:
            click.secho(f"Found {len(logs)} log entries:", fg="bright_green")
            for log in logs:
                click.secho(f"  • {log}", fg="bright_blue")
        else:
            click.secho(f"No logs found for {pipeline_id}.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--task_id', type=int, required=True, help='Task ID')
def results(task_id):
    """Display results for a specific task."""
    click.secho(f"\nDisplaying Results for Task {task_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        results = list(client[db_name]["task_results"].find({"task_id": task_id}))
        if results:
            click.secho(f"Found {len(results)} result(s):", fg="bright_green")
            for result in results:
                click.secho(f"  • {result}", fg="bright_blue")
        else:
            click.secho(f"No results found for task {task_id}.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@cli.command()
def list_pipelines():
    """List all pipelines in MongoDB."""
    click.secho("\nListing All Pipelines...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        pipelines = client[db_name]["schema_registry"].distinct("pipeline_id")
        if pipelines:
            click.secho(f"Found {len(pipelines)} pipeline(s):", fg="bright_green")
            for pipeline in pipelines:
                click.secho(f"  • {pipeline}", fg="bright_cyan")
        else:
            click.secho("No pipelines found.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return