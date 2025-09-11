import click
import os
import json
from datetime import datetime, timezone

# Directory where snapshots will be stored
SNAPSHOT_DIR = ".gitstack"
SNAPSHOT_FILE = os.path.join(SNAPSHOT_DIR, "snapshots.json")

def ensure_snapshot_dir():
    """Make sure the .gitstack/ folder exists."""
    if not os.path.exists(SNAPSHOT_DIR):
        os.makedirs(SNAPSHOT_DIR)

@click.group()
def main():
    """Gitstack CLI - An advanced modern version control system."""
    pass

@click.command()
def date():
    """Prints the current date and time."""
    now = datetime.now(timezone.utc)
    click.echo("Current date and time (UTC): {}".format(now.isoformat()))

@click.command()
def time():
    """Prints the current time."""
    now = datetime.now(timezone.utc)
    click.echo("Current time (UTC): {}".format(now.time().isoformat()))


@click.command()
def snap():
    """Captures current code, dependencies, and environment."""
    ensure_snapshot_dir()

    # List all files in current directory
    files = []
    for root, dirs, filenames in os.walk('.'):
        for f in filenames:
            if ".gitstack" not in root: # Avoid capturing our own metadata
                files.append(os.path.join(root, f))

    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }

    # Load existing snapshots or start afresh
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            data = json.load(f)

    else:
        data = []

    data.append(snapshot)

    # Save back to snapshots.json
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    click.echo("Snapshot taken! Total snapshots: {}".format(len(data)))

@click.command()
def restore():
    """Restore the last snapshot (just print files for now)."""
    if not os.path.exists(SNAPSHOT_FILE):
        click.echo("No snapshots found. Please take a snapshot first.")
        return
    
    with open(SNAPSHOT_FILE, "r") as f:
        data = json.load(f)

    if not data:
        click.echo("No snapshot saved yet.")
        return
    
    last_snapshot = data[-1]

    click.echo("Restoring snapshot from: {}".format(last_snapshot["timestamp"]))
    click.echo("Files included:")
    for f in last_snapshot["files"]:
        click.echo(f)



main.add_command(snap)
main.add_command(restore)
main.add_command(date)
main.add_command(time)

if __name__ == "__main__":
    main()