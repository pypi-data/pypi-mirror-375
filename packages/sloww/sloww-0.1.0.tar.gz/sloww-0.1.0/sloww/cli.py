import asyncio
import signal
import socket
import sys
from dataclasses import dataclass

import click

from sloww.proxy import SlowProxy
from sloww.constants import ByteSize


@dataclass
class Preset:
    speed: str
    delay: str


PRESETS = {
    "fast-4g": Preset(speed="9mb", delay="60ms"),
    "4g": Preset(speed="1.6mb", delay="150ms"),
    "3g": Preset(speed="500kb", delay="400ms"),
    "dialup": Preset(speed="56kb", delay="100ms"),
    "terrible": Preset(speed="10kb", delay="500ms"),
}

DEFAULT_BUFFER_SIZE = 8 * ByteSize.KB.value


def parse_speed(value):
    """Parse speed like '100kb', '1mb', '1000' (bytes)"""
    value = value.lower().strip()
    multipliers = {
        "kb": ByteSize.KB,
        "mb": ByteSize.MB,
        "gb": ByteSize.GB,
        "b": ByteSize.B,
    }

    for suffix, multiplier in multipliers.items():
        if value.endswith(suffix):
            num_part = value.replace(suffix, "")
            try:
                return int(float(num_part) * multiplier.value)
            except ValueError:
                raise click.BadParameter(f"Invalid speed: {value}")

    try:
        return int(value)
    except ValueError:
        raise click.BadParameter(f"Invalid speed: {value}")


def parse_delay(value):
    """Parse delay like '100ms', '1s', '0.5' (seconds)"""
    value = value.lower().strip()

    if value.endswith("ms"):
        try:
            return float(value[:-2]) / 1000
        except ValueError:
            raise click.BadParameter(f"Invalid delay: {value}")
    elif value.endswith("s"):
        try:
            return float(value[:-1])
        except ValueError:
            raise click.BadParameter(f"Invalid delay: {value}")
    else:
        try:
            return float(value)
        except ValueError:
            raise click.BadParameter(f"Invalid delay: {value}")


@click.command()
@click.argument("origin", metavar="[ADDR]:PORT")
@click.option(
    "-l",
    "--listen",
    default="127.0.0.1:RANDOM_PORT",
    metavar="[ADDR]:PORT",
    help="Listen address and port (the slowed-down version)",
)
@click.option(
    "-s",
    "--speed",
    default="0",
    metavar="SPEED",
    help="Speed limit (e.g., 100kb, 1mb, 1000) (default: unlimited)",
)
@click.option(
    "-d",
    "--delay",
    default="0",
    metavar="DELAY",
    help="Delay per packet (e.g., 100ms, 0.5s) (default: 0)",
)
@click.option(
    "-b",
    "--buffer-size",
    default=DEFAULT_BUFFER_SIZE,
    metavar="SIZE",
    help=f"Buffer size in bytes (default: {DEFAULT_BUFFER_SIZE})",
)
@click.option(
    "--preset",
    type=click.Choice(PRESETS),
    help="Use network preset",
)
@click.option(
    "--stats-interval",
    help="Print stats N minutes (default: disabled)",
    type=int,
    default=0,
)
@click.option(
    "--connect-timeout",
    help="Timeout for establishing a connection to the origin (default: 5)",
    type=int,
    default=5,
)
def main(
    origin, listen, speed, delay, buffer_size, preset, stats_interval, connect_timeout
):
    """
    Sloww - A slow TCP proxy for testing

    Forward TCP connections with configurable speed limits and delays.

    Examples:

    \b
    # Slow PostgreSQL on port 5432:
    sloww localhost:5432 -l :5433 -s 100kb -d 50ms

    \b
    # Simulate 3G connection:
    sloww example.com:80 --preset 3g

    \b
    # Custom slow proxy:
    sloww 192.168.1.100:3306 -s 1mb -d 100ms
    """

    # Apply presets
    if preset:
        preset_config = PRESETS[preset]
        speed = preset_config.speed
        delay = preset_config.delay
        click.echo(f"Using preset '{preset}': {speed} speed, {delay} delay")

    # Parse origin
    if ":" in origin:
        dest_addr, dest_port = origin.rsplit(":", 1)
        dest_port = int(dest_port)
        if not dest_addr:
            dest_addr = "127.0.0.1"
    else:
        raise click.BadParameter(f"{origin} must be in [ADDR]:PORT format")

    # Parse listen address
    if ":" in listen:
        listen_addr, listen_port = listen.rsplit(":", 1)
        listen_port = int(listen_port) if listen_port else 0
        if not listen_addr:
            listen_addr = "127.0.0.1"
    else:
        listen_addr = listen
        listen_port = 0

    # If port is 0, let the OS assign one
    if listen_port == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((listen_addr, 0))
            listen_port = s.getsockname()[1]

    # Parse speed and delay
    speed_limit = parse_speed(speed.lower())
    delay_seconds = parse_delay(delay.lower())

    proxy = SlowProxy(
        listen_addr=listen_addr,
        listen_port=listen_port,
        dest_addr=dest_addr,
        dest_port=dest_port,
        speed_limit=speed_limit,
        delay=delay_seconds,
        buffer_size=buffer_size,
        stats_interval=stats_interval,
        connect_timeout=connect_timeout,
    )

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        click.echo("\n[!] Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        click.echo("\n[!] Shutting down...")
