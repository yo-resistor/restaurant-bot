from pydantic import BaseModel


class RestaurantContext(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: str = ""
    tier: str = "regular"  # regular, vip

    def is_vip(self) -> bool:
        return self.tier == "vip"


class InputGuardRailOutput(BaseModel):
    is_off_topic: bool
    reason: str


class HandoffData(BaseModel):
    to_agent_name: str
    request_type: str
    request_description: str
    reason: str
