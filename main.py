from fastapi import FastAPI
from fastapi import staticfiles
from router.openaccount import router as openaccount_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from router.user import router as user_router
from router.transcation import router as transcation_router
from router.profile import router as profile_router
from router.setpin import router as router_pin


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
app.include_router(user_router)
app.include_router(transcation_router)
app.include_router(profile_router)
app.include_router(router_pin)


@app.get("/")
def home_views():
    return {"message": "Welcome to our home page"}
