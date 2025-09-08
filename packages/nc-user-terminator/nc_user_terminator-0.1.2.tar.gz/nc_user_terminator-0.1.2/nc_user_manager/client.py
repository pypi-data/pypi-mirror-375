import asyncio
from typing import Optional, Dict, Any

from models import UserResponse, OAuth2AuthorizeResponse, CallbackResponse
from exceptions import OAuthError
from utils import request


TENANT_HEADER = "X-Tenant-Code"


class OAuthClient:
    def __init__(
        self,
        base_url: str,
        tenant_code: str,
        redirect_url: Optional[str] = None,
        single_session: bool = False,
    ):
        """
        OAuth 客户端

        :param base_url: 服务端基础地址 (例如 http://localhost:8000)
        :param tenant_code: 租户编码
        :param redirect_url: 可选，重定向地址
        :param single_session: 是否单会话登录
        """
        self._base_url = base_url.rstrip("/")
        self._tenant_code = tenant_code
        self._redirect_url = redirect_url
        self._single_session = single_session

    # ----------------------
    # 内部异步包装
    # ----------------------
    async def _arequest(self, *args, **kwargs) -> dict:
        return await asyncio.to_thread(request, *args, **kwargs)

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {TENANT_HEADER: self._tenant_code}
        if extra:
            headers.update(extra)
        return headers

    # ----------------------
    # 授权
    # ----------------------
    def authorize(self, platform: str) -> OAuth2AuthorizeResponse:
        """同步获取授权地址"""
        params = {}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/authorize",
            params=params,
            headers=self._headers(),
        )
        return OAuth2AuthorizeResponse(res_dict)

    async def authorize_async(self, platform: str) -> OAuth2AuthorizeResponse:
        """异步获取授权地址"""
        params = {}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/authorize",
            params=params,
            headers=self._headers(),
        )
        return OAuth2AuthorizeResponse(res_dict)

    # ----------------------
    # 普通回调
    # ----------------------
    def callback(self, platform: str, query_params: Dict[str, Any]) -> CallbackResponse:
        """同步处理 OAuth2 回调 (非 One Tap)"""
        if query_params.get("credential"):
            raise OAuthError("Use google_one_tap() for One Tap login")

        params = {"single_session": str(self._single_session).lower()}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        params.update(query_params or {})
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    async def callback_async(self, platform: str, query_params: Dict[str, Any]) -> CallbackResponse:
        """异步处理 OAuth2 回调 (非 One Tap)"""
        if query_params.get("credential"):
            raise OAuthError("Use google_one_tap_async() for One Tap login")

        params = {"single_session": str(self._single_session).lower()}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        params.update(query_params or {})
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/{platform}/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    # ----------------------
    # Google One Tap
    # ----------------------
    def google_one_tap(self, credential: str) -> CallbackResponse:
        """同步 Google One Tap 登录"""
        params = {"credential": credential}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = request(
            "GET",
            f"{self._base_url}/api/oauth/google/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    async def google_one_tap_async(self, credential: str) -> CallbackResponse:
        """异步 Google One Tap 登录"""
        params = {"credential": credential}
        if self._redirect_url:
            params["redirect_url"] = self._redirect_url
        res_dict = await self._arequest(
            "GET",
            f"{self._base_url}/api/oauth/google/callback",
            params=params,
            headers=self._headers(),
        )
        return CallbackResponse(res_dict)

    # ----------------------
    # 获取用户信息
    # ----------------------
    def say_my_name(self, token: str) -> UserResponse:
        """同步获取当前用户"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        res_dict = request("GET", f"{self._base_url}/api/me", headers=headers)
        return UserResponse(res_dict)

    async def say_my_name_async(self, token: str) -> UserResponse:
        """异步获取当前用户"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        res_dict = await self._arequest("GET", f"{self._base_url}/api/me", headers=headers)
        return UserResponse(res_dict)

    # 刷新过期时间
    def reborn(self, token: str, extend_seconds: Optional[int] = None) -> dict:
        """重新设置过期时间"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        if extend_seconds:
            return request("POST", f"{self._base_url}/api/refresh-me", headers=headers, json_body={"extend_seconds": extend_seconds})
        else:
            return request("POST", f"{self._base_url}/api/refresh-me", headers=headers)

    async def reborn_async(self, token: str, extend_seconds: Optional[int] = None) -> dict:
        """异步重新设置过期时间"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        if extend_seconds:
            return await self._arequest("POST", f"{self._base_url}/api/refresh-me", headers=headers, json_body={"extend_seconds": extend_seconds})
        else:
            return await self._arequest("POST", f"{self._base_url}/api/refresh-me", headers=headers)

    # 登出
    def logout(self, token: str):
        headers = self._headers({"Authorization": f"Bearer {token}"})
        return request("POST", f"{self._base_url}/api/auth/logout", headers=headers)

    async def logout_async(self, token: str) -> dict:
        """异步获取当前用户"""
        headers = self._headers({"Authorization": f"Bearer {token}"})
        return await self._arequest("POST", f"{self._base_url}/api/auth/logout", headers=headers)