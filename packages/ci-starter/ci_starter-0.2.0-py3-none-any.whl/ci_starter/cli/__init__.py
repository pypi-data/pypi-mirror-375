from logging import getLogger
from logging.config import dictConfig as configure_logging
from pathlib import Path

from click import Path as ClickPath
from click import argument, command, echo, option

from .. import __version__ as version
from ..logging_conf import logging_configuration
from .callbacks import set_workdir
from .validations import validate_test_group, validate_workflow_file_name

configure_logging(logging_configuration)

logger = getLogger(__name__)


@command()
@option(
    "-C",
    "--change-dir",
    "workdir",
    default=".",
    type=ClickPath(exists=True, dir_okay=True, writable=True, allow_dash=False, path_type=Path),
    callback=set_workdir,
)
@argument("package_name")
@argument("module_name")
@option(
    "--workflow-file-name",
    default="continuous_delivery.yml",
    type=ClickPath(writable=True, path_type=Path),
    callback=validate_workflow_file_name,
)
@option("--test-group", default="test", callback=validate_test_group)
@option("--test-command", default="uv run -- pytest --verbose")
def cli(
    workdir: Path,
    module_name: str,
    package_name: str,
    workflow_file_name: Path,
    test_group: str,
    test_command: str,
) -> None:
    echo(f"Hello from ci-starter version {version}!")
    logger.debug("package_name = %s", package_name)
    logger.debug("module_name = %s", module_name)
    logger.debug("workflow_file_name = %s", workflow_file_name)
    logger.debug("workdir = %s", workdir)
    logger.debug("test_group = %s", test_group)
    logger.debug("test_command = %s", test_command)
