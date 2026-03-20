"""Web server command."""

import click

from .base import ensure_initialized


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
@click.option("--port", "-p", default=8000, type=int, help="Port to bind to (default: 8000)")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool):
    """Start the web server.

    Launches the orca-lift web interface on the specified host and port.
    Open your browser to the URL shown to access the web UI.

    Examples:

        # Start on default port (8000)
        orca-lift serve

        # Start on custom port
        orca-lift serve --port 3000

        # Expose to network (all interfaces)
        orca-lift serve --host 0.0.0.0

        # Development mode with auto-reload
        orca-lift serve --reload
    """
    ensure_initialized(ctx)

    import uvicorn

    from ..web import create_app

    click.echo()
    click.echo(click.style("Starting orca-lift web server...", fg="green"))
    click.echo()
    click.echo(f"  Local:   http://{host}:{port}")
    if host == "0.0.0.0":
        import socket
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
            click.echo(f"  Network: http://{local_ip}:{port}")
        except socket.gaierror:
            pass
    click.echo()
    click.echo("Press Ctrl+C to stop the server.")
    click.echo()

    # Create app
    app = create_app()

    # Run server
    uvicorn.run(
        app if not reload else "orca_lift.web:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=reload,
    )
