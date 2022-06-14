from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import api
from fastapi_cache.decorator import cache

from util.hierarchy import get_hierarchy, get_available_tags
from util.google import google_search

app = FastAPI()

app.include_router(api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


@app.get("/hierarchy")
@cache(expire=86400)
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
@cache(expire=86400)
async def generate_hierarchy():
    return get_available_tags()


@app.get("/search")
async def search_on_google(query: str = '', pages: int = 6):
    return google_search(query, pages)



if __name__ == "__main__":
    uvicorn.run(app, port=8000)
