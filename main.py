from fastapi import FastAPI
import uvicorn
from util.hierarchy import get_hierarchy

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# method='ward',

@app.get("/hierarchy")
async def generate_hierarchy(cuts=None, method: str = 'ward', metric: str = 'euclidean'):
    if cuts is None:
        cuts = [520]
    return get_hierarchy(cuts, method, metric)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
