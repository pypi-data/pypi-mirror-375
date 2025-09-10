from aiohttp import ClientSession

from zet.entities import News, Route, Stop, IncomingTrip, Trip, TripStop, Vehicle


async def get_newsfeed(session: ClientSession) -> list[News]:
    async with session.get("/NewsProxyService.Api/api/newsfeed") as response:
        response.raise_for_status()
        return await response.json()


async def get_routes(session: ClientSession) -> list[Route]:
    async with session.get("/TimetableService.Api/api/gtfs/routes") as response:
        response.raise_for_status()
        return await response.json()


async def get_stops(session: ClientSession) -> list[Stop]:
    async with session.get("/TimetableService.Api/api/gtfs/stops") as response:
        response.raise_for_status()
        return await response.json()


async def get_route_trips(session: ClientSession, route_id: str) -> list[Trip]:
    params = {"routeId": route_id, "daysFromToday": "0"}
    async with session.get("/TimetableService.Api/api/gtfs/routeTrips", params=params) as response:
        response.raise_for_status()
        return await response.json()


async def get_vehicles(session: ClientSession) -> list[Vehicle]:
    async with session.get("/TransportService.Api/api/Vehicle") as response:
        response.raise_for_status()
        return await response.json()


async def get_incoming_trips(session: ClientSession, stop_id: str) -> list[IncomingTrip]:
    path = "/TimetableService.Api/api/gtfs/stopIncomingTrips"
    params = {"stopId": stop_id, "isMapView": "false"}
    async with session.get(path, params=params) as response:
        return await response.json()


async def get_trip_stop_times(session: ClientSession, trip_id: str) -> list[TripStop]:
    path = "/TimetableService.Api/api/gtfs/tripStopTimes"
    params = {"tripId": trip_id, "daysFromToday": 0}
    async with session.get(path, params=params) as response:
        return await response.json()
