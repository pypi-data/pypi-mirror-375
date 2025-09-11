"""CLI initialization command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import getpass
import os
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.text import Text

from glaip_sdk import Client
from glaip_sdk._version import __version__ as _SDK_VERSION
from glaip_sdk.branding import AIPBranding

console = Console()


@click.command()
def init_command():
    """Initialize AIP project configuration."""
    # Display AIP welcome banner
    branding = AIPBranding.create_from_sdk(
        sdk_version=_SDK_VERSION, package_name="glaip-sdk"
    )
    branding.display_welcome_panel(title="🚀 AIP Initialization")

    # Get configuration
    console.print("\n[bold]API Configuration[/bold]")
    console.print("─" * 50)

    console.print(
        "\n[cyan]AIP API URL[/cyan] (default: https://your-aip-instance.com):"
    )
    api_url = input("> ").strip()
    if not api_url:
        api_url = "https://your-aip-instance.com"

    console.print("\n[cyan]AIP API Key[/cyan]:")
    api_key = getpass.getpass("> ")

    # Create config directory
    config_dir = Path.home() / ".aip"
    try:
        config_dir.mkdir(exist_ok=True)
    except Exception as e:
        console.print(Text(f"⚠️  Warning: Could not create config directory: {e}"))
        return

    # Save configuration
    config = {"api_url": api_url, "api_key": api_key}
    config_file = config_dir / "config.yaml"
    try:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        console.print(Text(f"⚠️  Warning: Could not save configuration: {e}"))
        return

    # Set secure file permissions (0600) - best effort on all platforms
    try:
        os.chmod(config_file, 0o600)
    except Exception:
        pass  # Ignore permission errors

    console.print(Text(f"\n✅ Configuration saved to: {config_file}"))

    # Test the new configuration
    console.print("\n🔌 Testing connection...")
    try:
        # Set environment variables
        os.environ["AIP_API_URL"] = api_url
        os.environ["AIP_API_KEY"] = api_key

        client = Client()
        agents = client.list_agents()
        console.print(Text(f"✅ Connection successful! Found {len(agents)} agents"))
    except Exception as e:
        console.print(Text(f"⚠️  Connection established but API call failed: {e}"))
        console.print(
            Text("   You may need to check your API permissions or network access")
        )

    console.print("\n🎉 [bold green]AIP initialization complete![/bold green]")
    console.print(f"📁 Configuration: {config_file}")
    console.print("💡 Next steps:")
    console.print("   • Run 'aip agents list' to see your agents")
    console.print("   • Run 'aip tools list' to see your tools")
    console.print("   • Run 'aip status' to check connection")
