from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from util.hierarchy import get_hierarchy, get_available_tags


app = FastAPI()


origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# method='ward',

@app.get("/hierarchy")
async def generate_hierarchy(cuts=None, method: str = 'ward', metric: str = 'euclidean'):
    if cuts is None:
        cuts = [520]

    return get_hierarchy(cuts, method, metric)


@app.get("/tags")
async def generate_hierarchy():
    return get_available_tags()


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
