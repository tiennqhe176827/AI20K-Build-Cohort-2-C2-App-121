from pydantic import BaseModel


class AdminStats(BaseModel):
    total_users: int
    total_notes: int
    active_users: int


class AdminUserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}
