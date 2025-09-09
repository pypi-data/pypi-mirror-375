from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import  JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

class OIDC:
    def __init__(self, app=None, *, client_id, client_secret, issuer, redirect_uri, session_secret, auto_login=False, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.issuer = issuer
        self.redirect_uri = redirect_uri
        self.auto_login = auto_login
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
            app.add_middleware(SessionMiddleware, secret_key=session_secret, same_site="lax")
            app.include_router(self.router, prefix="/auth")

    def _add_routes(self):
        @self.router.get("/login")
        async def login(request: Request, next: str = "/"):
            request.session['next_url'] = next
            return await self.oauth.oidc.authorize_redirect(request, self.redirect_uri)

        @self.router.get("/callback")
        async def callback(request: Request):
            token = await self.oauth.oidc.authorize_access_token(request)
            request.session["access_token"] = token['access_token']
            if self.auto_login and 'next_url' in request.session:
                next_url = request.session.pop('next_url', '/')
                return RedirectResponse(url=next_url, status_code=303)
            return JSONResponse(token)

        @self.router.get("/userinfo")
        async def userinfo(request: Request):
            token = {"access_token": self._get_token_from_request(request)}
            userinfo = await self.oauth.oidc.userinfo(token=token)
            return userinfo

    def _get_token_from_request(self, request: Request) -> str:
        auth_header = request.session.get("access_token")
        if not auth_header :
            if self.auto_login:
                raise HTTPException(status_code=303, detail="Redirecting to login", headers={"Location": "/auth/login?next=" + str(request.url.path)})
            else:
                raise HTTPException(status_code=401, detail="Missing token")
        return auth_header

    async def current_user(self, request: Request):
        token = {"access_token": self._get_token_from_request(request)}
        return await self.oauth.oidc.userinfo(token=token)
    
    async def require_oidc(self,request: Request):
        try:
            user = await self.current_user(request)
        except Exception as e:
            if self.auto_login:
                raise HTTPException(status_code=303, detail="Redirecting to login", headers={"Location": "/auth/login?next=" + str(request.url.path)})
            raise HTTPException(status_code=401, detail="Unauthorized") from e
        if user is None:
            if self.auto_login:
                raise HTTPException(status_code=303, detail="Redirecting to login", headers={"Location": "/auth/login?next=" + str(request.url.path)})
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    
    def require_oidc_group(self, group: str):
        async def dependency(request: Request):
            user = await self.require_oidc(request)
            if group not in user.get('groups', []):
                raise HTTPException(status_code=403, detail="Forbidden")
            return user
        return dependency