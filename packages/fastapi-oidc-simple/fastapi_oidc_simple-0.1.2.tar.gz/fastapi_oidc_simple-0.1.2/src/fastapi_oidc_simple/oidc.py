from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import  JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

class OIDC:
    def __init__(self, app=None, *, client_id, client_secret, issuer, redirect_uri, session_secret, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer = issuer
        self.redirect_uri = redirect_uri
        self.discovery_url = f"{issuer}/.well-known/openid-configuration"

        self.oauth = OAuth()
        self.oauth.register(
            name="oidc",
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=self.discovery_url,
            client_kwargs={"scope": scopes or "openid email profile"},
        )

        self.router = APIRouter()
        self._add_routes()

        if app:
            app.add_middleware(SessionMiddleware, secret_key=session_secret)
            app.include_router(self.router, prefix="/auth")

    def _add_routes(self):
        @self.router.get("/login")
        async def login(request: Request):
            return await self.oauth.oidc.authorize_redirect(request, self.redirect_uri)

        @self.router.get("/callback")
        async def callback(request: Request):
            token = await self.oauth.oidc.authorize_access_token(request)
            request.session["user"] = token
            return JSONResponse(token)

        @self.router.get("/userinfo")
        async def userinfo(request: Request):
            token = {"access_token": self._get_token_from_request(request)}
            userinfo = await self.oauth.oidc.userinfo(token=token)
            return userinfo

    def _get_token_from_request(self, request: Request) -> str:
        auth_header = request.session.get("user")
        if not auth_header or not "access_token" in auth_header:
            raise HTTPException(status_code=401, detail="Missing token")
        return auth_header["access_token"]

    async def current_user(self, request: Request):
        token = {"access_token": self._get_token_from_request(request)}
        return await self.oauth.oidc.userinfo(token=token)
    
    async def require_oidc(self,request: Request):
        try:
            user = await self.current_user(request)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Unauthorized") from e
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    
    def require_oidc_group(self, group: str):
        async def dependency(request: Request):
            user = await self.require_oidc(request)
            if group not in user.get('groups', []):
                raise HTTPException(status_code=403, detail="Forbidden")
            return user
        return dependency