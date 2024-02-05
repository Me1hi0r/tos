from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from clickhouse_driver import Client
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# origins = [
#
#     "http://localhost:8000",
#     "http://localhost:9000",
#     "http://0.0.0.0:9000",
#     "http://localhost:7777",
#     "google.com"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ch_client = Client(host='tos-click', port=9000)


@app.post("/tos")
async def save_session_time(req: Request):
    log = await req.json()
    session = log["session"]
    host = log["host"]
    tos = log["time"]

    print(log)

    # Query ClickHouse for user data
    query = f" INSERT INTO metric.tos VALUES ('{session}', '{host}', {tos}, now() )"
    result = ch_client.execute(query)
    print(result)

    if result:
        # Convert ClickHouse result to JSON and return it
        user_data = result[0]  # Assuming the result is a dictionary
        return JSONResponse(content=user_data)
    else:
        return JSONResponse(content={"message": "User not found"}, status_code=404)



@app.get('/tos')
async def get_logs():

    query = f"SELECT * FROM metric.tos"
    result = ch_client.execute(query)
    # return JSONResponse(content=result)
    return JSONResponse(jsonable_encoder(result))

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=9009, reload=True)
