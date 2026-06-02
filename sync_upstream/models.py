from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RepositoryConfig:
    name: str
    branches: List[str] = field(default_factory=list)


@dataclass
class AutoScanConfig:
    enabled: bool = True
    include_private: bool = False


@dataclass
class SyncConfig:
    method: str = "api"
    timeout: int = 300


@dataclass
class AppConfig:
    github_token: str
    owner: Optional[str] = None
    auto_scan: AutoScanConfig = field(default_factory=AutoScanConfig)
    repositories: dict = field(default_factory=lambda: {"included": [], "excluded": []})
    sync: SyncConfig = field(default_factory=SyncConfig)


@dataclass
class Repository:
    owner: str
    name: str
    full_name: str
    is_private: bool
    has_upstream: bool = False
    upstream: Optional[str] = None
    default_branch: str = "master"
