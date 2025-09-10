from typing import Optional

class OAuth2AuthorizeResponse(dict):
    @property
    def url(self) -> str:
        return self.get("authorization_url")

class UserResponse(dict):
    @property
    def id(self) -> str:
        return self.get("id")

    @property
    def email(self) -> str:
        return self.get("email")

    @property
    def picture(self) -> Optional[str]:
        return self.get("picture")

    @property
    def full_name(self) -> Optional[str]:
        return self.get("full_name")

    @property
    def role(self) -> Optional[str]:
        return self.get("role")

class CallbackResponse(dict):
    @property
    def token(self) -> str:
        return self.get("access_token")

    @property
    def token_type(self) -> str:
        return self.get("token_type")

    @property
    def user_name(self) -> str:
        return self.get("user_name")

    @property
    def email(self) -> str:
        return self.get("email")

    @property
    def user_picture(self) -> str:
        return self.get("user_picture")
