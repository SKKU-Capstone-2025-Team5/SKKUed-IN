from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, profile, message, websocket, team, notification, contest, uploads, recommend

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(message.router, prefix="/messages", tags=["messages"])
api_router.include_router(websocket.router, prefix="/ws", tags=["ws"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
api_router.include_router(recommend.router, prefix="/recsys", tags=["recsys"]) #변경
api_router.include_router(team.router, prefix="/teams", tags=["teams"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(contest.router, prefix="/contests", tags=["contests"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])