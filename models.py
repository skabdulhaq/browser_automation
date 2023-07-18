from pydantic import BaseModel
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = True
    active_containers: Union[int, None] = 0
    max_containers: Union[int, None] = 1
    containers: Union[dict, None] = {}

class Container(BaseModel):
    container_image: Union[str, None] = None
    password: Union[str, None] = None
    port: Union[int, None] = None

class UserInDB(User):
    hashed_password: str

class ContainerInDB(Container):
    server_name: Union[str, None] = None
    up_time: Union[str, None] = None
    status: Union[str, None] = None
    server_ip:Union[str, None] = None
    service_url:Union[str, None] = None

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Union[str, None] = None
    password: str
