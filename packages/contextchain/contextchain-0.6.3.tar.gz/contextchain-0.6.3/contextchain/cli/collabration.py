#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from .main_1 import cli
from .main_1 import get_mongo_client


@cli.command()
def ccshare_init():
    """Initialize a .ccshare file for collaborative MongoDB Atlas access."""
    click.secho("\nInitializing .ccshare File...", fg="bright_yellow", bold=True)
    ccshare = {
        "uri": click.prompt(click.style("MongoDB Atlas URI", fg="bright_blue"), default="mongodb+srv://user:pass@cluster0.mongodb.net"),
        "db_name": click.prompt(click.style("Database name", fg="bright_blue"), default="contextchain_db"),
        "roles": []
    }
    while click.confirm(click.style("Add a user role?", fg="bright_blue")):
        user = click.prompt(click.style("Username", fg="bright_blue"))
        role = click.prompt(click.style("Role", fg="bright_blue"), default="readOnly", type=click.Choice(["readOnly", "readWrite"]))
        ccshare["roles"].append({"user": user, "role": role})
    output_path = Path("config/team.ccshare")
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w") as f:
        yaml.safe_dump(ccshare, f)
    click.secho(f"✓ .ccshare file created: {output_path}", fg="bright_green", bold=True)

@cli.command()
@click.option('--uri', required=True, help='MongoDB Atlas URI')
def ccshare_join(uri):
    """Join an existing .ccshare collaboration."""
    click.secho("\nJoining .ccshare Collaboration...", fg="bright_yellow", bold=True)
    ccshare = {
        "uri": uri,
        "db_name": click.prompt(click.style("Database name", fg="bright_blue"), default="contextchain_db"),
        "roles": [{
            "user": click.prompt(click.style("Username", fg="bright_blue")), 
            "role": click.prompt(click.style("Role", fg="bright_blue"), default="readOnly", type=click.Choice(["readOnly", "readWrite"]))
        }]
    }
    output_path = Path("config/team.ccshare")
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w") as f:
        yaml.safe_dump(ccshare, f)
    click.secho(f"✓ Joined collaboration: {output_path}", fg="bright_green", bold=True)

@cli.command()
def ccshare_status():
    """Check the status of the .ccshare configuration."""
    click.secho("\nChecking .ccshare Status...", fg="bright_yellow", bold=True)
    ccshare_path = Path("config/team.ccshare")
    if ccshare_path.exists():
        try:
            with ccshare_path.open("r") as f:
                ccshare = yaml.safe_load(f)
            client = get_mongo_client(ccshare["uri"])
            client.server_info()
            click.secho(f"✓ Connected to MongoDB", fg="bright_green", bold=True)
            click.secho(f"  Database: {ccshare['db_name']}", fg="bright_cyan")
            click.secho(f"  Roles: {ccshare['roles']}", fg="bright_cyan")
        except Exception as e:
            click.secho(f"✗ Connection error: {e}", fg="red", bold=True)
            return
    else:
        click.secho("✗ No .ccshare file found.", fg="red", bold=True)
        return