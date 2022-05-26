from fastapi import FastAPI, HTTPException
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
async def generate_hierarchy(cuts: int = None, method: str = 'ward', metric: str = 'euclidean'):
    if cuts is None:
        cuts = [520]

    cuts_list = []
    if cuts == 0 or cuts == 1:
        cuts_list.append(1)
    else:
        while cuts > 0:
            if 200 < cuts < 600:
                cuts -= 15
            elif 100 < cuts < 200:
                cuts -= 10
            elif 50 < cuts < 100:
                cuts -= 5
            elif 10 < cuts < 50:
                cuts -= 3
            elif cuts < 10:
                cuts -= 1
            else:
                cuts -= 1

            if cuts <= 0:
                break

            cuts_list.append(cuts)

    val = None

    try:
        val = get_hierarchy(cuts_list, method, metric)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=e.__str__())

    # print(cuts_list)
    return val


@app.get("/tags")
async def generate_hierarchy():
    return get_available_tags()


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
