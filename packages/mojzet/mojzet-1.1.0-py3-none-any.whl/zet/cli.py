import logging
import textwrap

from aiohttp import ClientSession
import click

from zet import api, __version__
from zet.app import ZetApp
from zet.decorators import async_command, pass_session
from zet.entities import Stop
from zet.output import format_direction, format_route_type, format_time, format_tracked, table_dump


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option(__version__)
def zet(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@zet.command()
@async_command
@pass_session
async def news(session):
    """Show news feed"""
    news = await api.get_newsfeed(session)

    def _generator():
        first = True
        for item in news:
            if not first:
                yield click.style("-" * 80, dim=True) + "\n\n"
            yield click.style(item["title"], bold=True) + "\n\n"
            for line in textwrap.wrap(item["description"], 80):
                yield line + "\n"
            yield "\n"
            yield click.style(item["link"], underline=True, dim=True) + "\n"
            yield click.style(item["datePublished"], dim=True) + "\n\n"
            first = False

    click.echo_via_pager(_generator())


@zet.command()
@async_command
@pass_session
async def tui(session):
    app = ZetApp(session)
    await app.run_async()


@zet.command()
@click.option("-p", "--pager/--no-pager")
@async_command
@pass_session
async def routes(session, pager: bool):
    """List routes"""
    routes = await api.get_routes(session)

    table_dump(
        routes,
        {
            "Type": lambda r: format_route_type(r["routeType"]),
            "No": lambda r: str(r["id"]),
            "From": lambda r: r["departureHeadsign"],
            "To": lambda r: r["destinationHeadsign"],
        },
        pager=pager,
    )


@zet.command()
@click.option("-p", "--pager/--no-pager")
@async_command
@pass_session
async def stops(session, pager: bool):
    """List stops"""
    stops = await api.get_stops(session)

    table_dump(
        stops,
        {
            "ID": lambda s: str(s["id"]),
            "Name": lambda s: s["name"],
            "Latitude": lambda s: str(s["stopLat"]),
            "Longitude": lambda s: str(s["stopLong"]),
            "Type": lambda s: format_route_type(s["routeType"]),
            "Trips": lambda s: _trips(s),
        },
        pager=pager,
    )


def _trips(stop: Stop):
    return ", ".join(trip["routeCode"] for trip in stop["trips"])


@zet.command()
@click.argument("stop_id")
@click.option("-p", "--pager/--no-pager")
@click.option("-r", "--route", "route_id")
@async_command
@pass_session
async def trips(session, stop_id: str, pager: bool, route_id: str):
    """List arrivals for a given stop"""
    trips = await api.get_incoming_trips(session, stop_id)

    if route_id:
        trips = [t for t in trips if t["routeShortName"] == route_id]

    table_dump(
        trips,
        {
            "#": lambda t: t["routeShortName"],
            "Destination": lambda t: t["headsign"],
            "Arrival": lambda t: format_time(t["expectedArrivalDateTime"]),
            "Tracked?": lambda t: format_tracked(t["hasLiveTracking"]),
        },
        pager=pager,
    )


@zet.command()
@click.argument("trip_id")
@click.option("-p", "--pager/--no-pager")
@async_command
@pass_session
async def trip_stops(session, trip_id: str, pager: bool):
    """List stops for a given trip"""
    trips = await api.get_trip_stop_times(session, trip_id)

    table_dump(
        trips,
        {
            "#": lambda t: str(t["id"]),
            "Stop": lambda t: t["stopName"],
            "Arrival": lambda t: format_time(t["expectedArrivalDateTime"]),
            "Arrived?": lambda t: str(t["isArrived"]),
            "Predict?": lambda t: str(t["isArrivedPrediction"]),
        },
        pager=pager,
    )


@zet.command()
@click.argument("route_id")
@click.option("-p", "--pager/--no-pager")
@click.option(
    "-d",
    "--direction",
    type=click.Choice(["A", "B"], case_sensitive=False),
    help="Show only trips in the given direction",
)
@async_command
@pass_session
async def route_trips(session, route_id: str, pager: bool, direction: str | None):
    """List trips for a given route"""
    trips = await api.get_route_trips(session, route_id)

    if direction == "A":
        trips = [t for t in trips if t["direction"] == 0]

    if direction == "B":
        trips = [t for t in trips if t["direction"] == 1]

    table_dump(
        trips,
        {
            "Trip ID": lambda t: str(t["id"]),
            "Direction": lambda t: format_direction(t["direction"]),
            "Headsign": lambda t: t["headsign"],
            "Depart": lambda t: format_time(t["departureDateTime"]),
            "Arrive": lambda t: format_time(t["arrivalDateTime"]),
            "Tracked?": lambda t: str(t["hasLiveTracking"]),
        },
        pager=pager,
    )


@zet.command()
@click.option("-p", "--pager/--no-pager")
@async_command
@pass_session
async def vehicles(session: ClientSession, pager: bool):
    """List vehicles"""
    vehicles = await api.get_vehicles(session)

    table_dump(
        vehicles,
        {
            "#": lambda x: str(x["id"]),
            "Garage#": lambda x: x["garageNumber"],
            "Plate": lambda x: x["numberPlate"] or "",
            "Description": lambda x: x["description"],
        },
        pager=pager,
    )
