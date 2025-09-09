"""HoloViz MCP Server.

This MCP server provides comprehensive tools, resources and prompts for working with the HoloViz ecosystem,
including Panel and hvPlot following best practices.

The server is composed of multiple sub-servers that provide various functionalities:

- Documentation: Search and access HoloViz documentation as context
- hvPlot: Tools, resources and prompts for using hvPlot to develop quick, interactive plots in Python
- Panel: Tools, resources and prompts for using Panel Material UI
"""

import asyncio
import logging
import os

from fastmcp import FastMCP

from holoviz_mcp.config.loader import get_config
from holoviz_mcp.docs_mcp.server import mcp as docs_mcp
from holoviz_mcp.hvplot_mcp.server import mcp as hvplot_mcp
from holoviz_mcp.panel_mcp.server import mcp as panel_mcp

logger = logging.getLogger(__name__)

mcp: FastMCP = FastMCP(
    name="holoviz",
    instructions="""
    [his MCP server provides comprehensive tools, resources and prompts for working with the HoloViz ecosystem following best practices.

    HoloViz provides a set of core Python packages that make visualization easier, more accurate, and more powerful:

    - [Panel](https://panel.holoviz.org): for making apps and dashboards for your plots from any supported plotting library.
    - [hvPlot](https://hvplot.holoviz.org): to quickly generate interactive plots from your data.
    - [HoloViews](https://holoviews.org): to help you make all of your data instantly visualizable.
    - [GeoViews](https://geoviews.org): to extend HoloViews for geographic data.
    - [Datashader](https://datashader.org): for rendering even the largest datasets.
    - [Lumen](https://lumen.holoviz.org): to build data-driven dashboards from a simple YAML specification that's well suited to modern AI tools like LLMs.
    - [Param](https://param.holoviz.org): to create declarative user-configurable objects.
    - [Colorcet](https://colorcet.holoviz.org): for perceptually uniform colormaps.

    The server is composed of multiple sub-servers that provide various functionalities:

    - Documentation: Search and access HoloViz documentation and reference guides
    - Panel: Tools, resources and prompts for using Panel and Panel Extension packages
    - hvPlot: Tools, resources and prompts for using hvPlot to develop quick, interactive plots in Python
    """,
)


async def setup_composed_server() -> None:
    """Set up the composed server by importing all sub-servers with prefixes.

    This uses static composition (import_server), which copies components
    from sub-servers into the main server with appropriate prefixes.
    """
    await mcp.import_server(docs_mcp, prefix="docs")
    await mcp.import_server(hvplot_mcp, prefix="hvplot")
    await mcp.import_server(panel_mcp, prefix="panel")


def main() -> None:
    """Set up and run the composed MCP server."""
    pid = f"Process ID: {os.getpid()}"
    print(pid)  # noqa: T201

    async def setup_and_run() -> None:
        await setup_composed_server()
        config = get_config()
        await mcp.run_async(transport=config.server.transport)

    asyncio.run(setup_and_run())


if __name__ == "__main__":
    # Run the composed MCP server
    main()
