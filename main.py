from fastapi import FastAPI
from fastapi import staticfiles
from router.openaccount import router as openaccount_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origin = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_origins=origin,
    allow_methods=["*"],
)


app.include_router(openaccount_router)


@app.get("/")
def home_views():
    return {"message": "Welcome to our home page"}
