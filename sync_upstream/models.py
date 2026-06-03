from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RepositoryConfig:
    name: str
    branches: List[str] = field(default_factory=list)  # Empty means only sync default branch


@dataclass
class AppConfig:
    github_token: str
    owner: Optional[str] = None
    repositories: List[RepositoryConfig] = field(default_factory=list)  # Must specify repositories


@dataclass
class Repository:
    owner: str
    name: str
    full_name: str
    is_private: bool
    has_upstream: bool = False
    upstream: Optional[str] = None
    default_branch: str = "master"
