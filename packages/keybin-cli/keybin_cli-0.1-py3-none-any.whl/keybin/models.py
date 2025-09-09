from pydantic import BaseModel

class passwordLog(BaseModel):
    logID : int | None = None
    service: str | None = None
    user : str | None = None
    email : str | None = None
    password : str | None = None
    tags : list[str]| None = None
    createdAt : str| None = None
    

class LogsFileModel(BaseModel):
    currentLogId : int
    logs : dict [int, passwordLog]

class ProfileModel(BaseModel):
    data_path: str
    encrypted : bool
    salt: str | None = None
    encrypted_dek: str | None = None

class ConfigDataModel(BaseModel):
    active_profile: str
    profiles: dict[str, ProfileModel]