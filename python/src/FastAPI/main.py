from fastapi import FastAPI

from smartphone_routers import router as smartphone_router
from routers.users import router as users_router
from routers.researches import router as researches_router
from routers.kits import router as kit_router
from routers.samples import router as samples_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(researches_router)
app.include_router(kit_router)
app.include_router(samples_router)
app.include_router(smartphone_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1337, reload=True)
