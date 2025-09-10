import asyncio
import sys
import time
import socket

import click

from sloww.constants import ByteSize


class SlowProxy:
    def __init__(
        self,
        listen_addr: str,
        listen_port: int,
        dest_addr: str,
        dest_port: int,
        speed_limit: float,
        delay: float,
        buffer_size,
        stats_interval: int = 0,
        connect_timeout: int = 5,
    ):
        self.listen_addr = listen_addr
        self.listen_port = listen_port
        self.dest_addr = dest_addr
        self.dest_port = dest_port
        self.speed_limit = speed_limit  # bytes per second
        self.delay = delay  # seconds
        self.buffer_size = buffer_size
        self.active_connections = 0
        self.total_bytes = 0
        self.start_time = time.time()
        self.stats_interval = stats_interval
        self.connect_timeout = connect_timeout

    async def handle_client(self, client_reader, client_writer):
        peer = client_writer.get_extra_info("peername")
        self.active_connections += 1
        click.echo(
            f"[+] Connection from {peer[0]}:{peer[1]} (active: {self.active_connections})"
        )

        dest_writer = None
        try:
            # Connect to destination with timeout
            dest_reader, dest_writer = await asyncio.wait_for(
                asyncio.open_connection(self.dest_addr, self.dest_port),
                timeout=self.connect_timeout,
            )

            # Start bidirectional forwarding; allow proper TCP half-close via shutdown
            t_c2d = asyncio.create_task(
                self.forward_data(client_reader, dest_writer, "→")
            )
            t_d2c = asyncio.create_task(
                self.forward_data(dest_reader, client_writer, "←")
            )
            await asyncio.gather(t_c2d, t_d2c)

        except asyncio.TimeoutError:
            click.echo(
                f"[!] Timeout connecting to {self.dest_addr}:{self.dest_port}",
                err=True,
            )
        except ConnectionRefusedError:
            click.echo(
                f"[!] Connection refused by {self.dest_addr}:{self.dest_port}",
                err=True,
            )
        except Exception as e:
            click.echo(f"[!] Error: {e}", err=True)
        finally:
            self.active_connections -= 1
            click.echo(
                f"[-] Disconnected {peer[0]}:{peer[1]} (active: {self.active_connections})"
            )

            if not client_writer.is_closing():
                client_writer.close()
                await client_writer.wait_closed()

            if dest_writer and not dest_writer.is_closing():
                dest_writer.close()
                try:
                    await dest_writer.wait_closed()
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    click.echo(
                        f"[-] Connection reset by {self.dest_addr}:{self.dest_port}"
                    )

    async def forward_data(self, reader, writer, direction):
        try:
            while True:
                data = await reader.read(self.buffer_size)
                if not data:
                    try:
                        sock = writer.get_extra_info("socket")
                        if sock is not None:
                            sock.shutdown(socket.SHUT_WR)
                    except OSError:
                        pass
                    return

                self.total_bytes += len(data)

                if self.delay > 0:
                    await asyncio.sleep(self.delay)

                if self.speed_limit > 0:
                    transfer_time = len(data) / self.speed_limit
                    start_time = time.time()
                    writer.write(data)
                    await writer.drain()
                    elapsed = time.time() - start_time
                    if elapsed < transfer_time:
                        await asyncio.sleep(transfer_time - elapsed)
                else:
                    writer.write(data)
                    await writer.drain()

        except asyncio.CancelledError:
            return
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) as e:
            click.echo(f"[!] Connection broken ({direction}): {e}", err=True)
        except Exception as e:
            click.echo(f"[!] Forward error ({direction}): {e}", err=True)

    async def show_stats(self):
        """Periodically show statistics"""
        while True:
            await asyncio.sleep(self.stats_interval * 60)  # Every N minute
            uptime = time.time() - self.start_time
            mb_transferred = self.total_bytes / ByteSize.MB.value
            click.echo(
                f"[i] Stats: {self.active_connections} connections, "
                f"{mb_transferred:.1f} MB transferred, "
                f"uptime {uptime/60:.0f}m"
            )

    async def start(self):
        try:
            server = await asyncio.start_server(
                self.handle_client, self.listen_addr, self.listen_port
            )
        except OSError as e:
            click.echo(
                f"Failed to bind to {self.listen_addr}:{self.listen_port}: {e}",
                err=True,
            )
            sys.exit(1)

        click.echo(click.style("Sloww - Slow TCP Proxy", bold=True))
        click.echo(f"Listening on: {self.listen_addr}:{self.listen_port}")
        click.echo(f"Forwarding to: {self.dest_addr}:{self.dest_port}")

        if self.speed_limit > 0:
            if self.speed_limit >= ByteSize.MB.value:
                speed_str = f"{self.speed_limit/ByteSize.MB.value:.1f} MB/s"
            elif self.speed_limit >= ByteSize.KB.value:
                speed_str = f"{self.speed_limit/ByteSize.KB.value:.1f} KB/s"
            else:
                speed_str = f"{self.speed_limit} B/s"
            click.echo(f"Speed limit: {speed_str}")
        else:
            click.echo("Speed limit: unlimited")

        if self.delay > 0:
            click.echo(f"Delay: {self.delay*1000:.0f}ms per packet")
        else:
            click.echo("Delay: none")

        click.echo(f"Buffer size: {self.buffer_size} bytes")
        click.echo("\nPress Ctrl+C to stop\n")

        if self.stats_interval:
            # Start stats task
            asyncio.create_task(self.show_stats())

        async with server:
            await server.serve_forever()
