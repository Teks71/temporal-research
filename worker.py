import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from cities_game.workflow import CityGameWorkflow


async def main() -> None:
    client = await Client.connect("localhost:7233")
    worker = Worker(client, task_queue="city-game", workflows=[CityGameWorkflow])
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
