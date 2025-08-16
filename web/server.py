from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio.client import Client, WorkflowAlreadyStartedError

from cities_game.workflow import CityGameWorkflow

app = FastAPI()

client: Client | None = None


class Move(BaseModel):
    city: str


@app.on_event("startup")
async def startup() -> None:
    global client
    client = await Client.connect("localhost:7233")


@app.post("/start")
async def start_game() -> dict:
    assert client
    try:
        await client.start_workflow(
            CityGameWorkflow.run,
            id="city-game",
            task_queue="city-game",
        )
    except WorkflowAlreadyStartedError:
        pass
    return await client.query_workflow("city-game", CityGameWorkflow.get_state)


@app.post("/move")
async def make_move(move: Move) -> dict:
    assert client
    try:
        await client.signal_workflow("city-game", CityGameWorkflow.user_move, move.city)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    return await client.query_workflow("city-game", CityGameWorkflow.get_state)


@app.post("/give_up")
async def give_up() -> dict:
    assert client
    await client.signal_workflow("city-game", CityGameWorkflow.give_up)
    return await client.query_workflow("city-game", CityGameWorkflow.get_state)
