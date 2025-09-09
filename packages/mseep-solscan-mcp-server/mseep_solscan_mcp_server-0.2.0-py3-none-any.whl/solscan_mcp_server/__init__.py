import logging

import click

from .server import serve


@click.command()
@click.option(
    "--api-key", "-k", type=str, envvar="SOLSCAN_API_KEY", help="Solscan Pro API key"
)
@click.option(
    "--transport",
    "-t",
    type=click.Choice(["sse", "stdio"]),
    default="sse",
    help="Transport protocol to use",
)
@click.option(
    "--host",
    "-h",
    type=str,
    default="127.0.0.1",
    help="Host to bind to when using SSE transport",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8050,
    help="Port to listen on when using SSE transport",
)
@click.option("-v", "--verbose", count=True)
def main(
    api_key: str | None, transport: str, host: str, port: int, verbose: bool
) -> None:
    """MCP Solscan Server - Solscan Pro API functionality for MCP"""
    import asyncio

    if not api_key:
        raise click.ClickException(
            "Solscan API key is required. Set it via --api-key or SOLSCAN_API_KEY environment variable"
        )

    log_level = logging.WARN
    if verbose:
        log_level = logging.DEBUG

    asyncio.run(
        serve(
            api_key=api_key,
            transport=transport,
            host=host,
            port=port,
            log_level=logging.getLevelName(log_level),
        )
    )


if __name__ == "__main__":
    main()
