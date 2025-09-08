from dataclasses import dataclass, field
from pathlib import Path

from click import Context, Parameter


@dataclass
class WorkDir:
    project: Path
    config: Path = field(init=False)
    workflows: Path = field(init=False)
    build: Path = field(init=False)
    release: Path = field(init=False)
    test_e2e: Path = field(init=False)

    def __post_init__(self):
        self.config = self.project / "semantic-release.toml"
        self.workflows = self.project / ".github" / "workflows"
        self.build = self.workflows / "build.yml"
        self.release = self.workflows / "release.yml"
        self.test_e2e = self.workflows / "test-e2e.yml"


def set_workdir(ctx: Context, _param: Parameter, path: Path) -> WorkDir:
    return WorkDir(path)
