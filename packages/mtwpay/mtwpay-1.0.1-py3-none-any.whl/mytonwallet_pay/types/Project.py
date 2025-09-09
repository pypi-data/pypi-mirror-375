from pydantic import BaseModel


class Project(BaseModel):
    name: str
    """Project name"""
    projectId: int
    """Project ID"""
    wallet: str
    """Project's wallet"""
