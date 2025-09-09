"""Freeze a python cell as schematic netlist."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from .app import app

if TYPE_CHECKING:
    import gdsfactory.get_netlist as gfn
    import gdsfactory.schematic as gfs
    import orjson
    from fastapi import Body
    from fastapi.responses import JSONResponse, PlainTextResponse

    import gdsfactoryplus.core.pdk as gfp_pdk
else:
    from gdsfactoryplus.core.lazy import lazy_import

    orjson = lazy_import("orjson")
    gfn = lazy_import("gdsfactory.get_netlist")
    gfs = lazy_import("gdsfactory.schematic")
    gfp_pdk = lazy_import("gdsfactoryplus.core.pdk", "gfp_pdk")


@app.post("/freeze/{cell_name}", response_model=None)
def freeze_post(
    cell_name: str,
    body: Annotated[str, Body()],
) -> PlainTextResponse | JSONResponse:
    """Freeze a python cell as schematic netlist.

    Args:
        cell_name: name of the cell to freeze.
        body: the keyword arguments to create the cell with.
    """
    from fastapi.responses import JSONResponse, PlainTextResponse

    pdk = gfp_pdk.get_pdk()
    if cell_name not in pdk.cells:
        msg = f"Cell {cell_name} not found in PDK {pdk.name}"
        return PlainTextResponse(msg, status_code=400)

    cell_func = pdk.cells[cell_name]
    if cell_func.__module__.endswith("_picyml"):
        msg = f"Cell {cell_name} is alreay a YAML cell."
        return PlainTextResponse(msg, status_code=422)

    kwargs = {} if not body else orjson.loads(body)
    cell = cell_func(**kwargs)

    net = gfn.get_netlist(cell, allow_multiple=False)
    if "warnings" in net:
        del net["warnings"]
    net = gfs.Netlist.model_validate(net)

    return JSONResponse(net.model_dump(), status_code=200)


@app.get("/freeze/{cell_name}", response_model=None)
def freeze_get(cell_name: str) -> PlainTextResponse | JSONResponse:
    """Freeze a python cell as schematic netlist.

    Args:
        cell_name: name of the cell to freeze.
    """
    return freeze_post(cell_name, body="")
