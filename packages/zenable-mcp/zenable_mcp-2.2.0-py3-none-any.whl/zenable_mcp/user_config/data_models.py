import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError

LOG = logging.getLogger(__name__)


class CheckConfig(BaseModel):
    """
    Configuration for the check command.

    Parameters:
        patterns:
            List of patterns to include files for checking. Supports:
            - Exact filename matches (e.g., "main.py")
            - Glob patterns (e.g., "**/*.py", "src/**/*.js")
            When invoked as a hook, these patterns act as filters for files passed by the IDE.
        exclude_patterns:
            List of patterns to exclude files from checking. Supports:
            - Exact filename matches (e.g., "test.py")
            - Glob patterns (e.g., "**/test_*.py", "**/*.test.js")
    """

    model_config = ConfigDict(strict=True, extra="allow")

    patterns: list[str]
    exclude_patterns: list[str]


class CommentsConfig(BaseModel):
    """
    Configuration for controlling which comments are posted during reviews.

    Parameters:
        taking_a_look:
            Whether to post the "Taking a look" comment at the start of reviews.
            Default: True (comment is posted)
        no_findings:
            Whether to post the "Nice work" comment when no issues are found.
            Default: True (comment is posted)
    """

    model_config = ConfigDict(strict=True, extra="allow")

    taking_a_look: bool = True
    no_findings: bool = True


class PRReviewsConfig(BaseModel):
    """
    Configuration for pull request reviews.

    Parameters:
        skip_filenames:
            Set of patterns to skip files. Supports:
            - Exact filename matches (e.g., "package-lock.json")
            - Glob patterns (e.g., "**/*.rbi", "foo/**/*.pyc")
            - Negation patterns with ! prefix (e.g., "!keep-this.json")
            Note: When using negation patterns, order matters - the last matching
            pattern wins. Consider using a list in config files to preserve order.
        skip_branches:
            Regex of branch names to skip. You can use python regex to match the branch names.
        comments:
            Configuration for controlling which comments are posted during reviews.
    """

    model_config = ConfigDict(strict=True, extra="allow")

    skip_filenames: list[str]
    skip_branches: set[str]
    comments: Optional[CommentsConfig] = None


class UserConfig(BaseModel):
    """
    Main user configuration model.
    """

    model_config = ConfigDict(strict=True, extra="allow")

    pr_reviews: PRReviewsConfig
    check: Optional[CheckConfig] = None


class CommentsTomlConfig(CommentsConfig):
    """
    Internal class modelling the representation of a comments config in a TOML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Everything is optional
    taking_a_look: Optional[bool] = None
    no_findings: Optional[bool] = None


class CheckTomlConfig(CheckConfig):
    """
    Internal class modelling the representation of a check config in a TOML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Everything is optional
    patterns: Optional[list[str]] = None
    exclude_patterns: Optional[list[str]] = None


class PRTomlConfig(PRReviewsConfig):
    """
    Internal class modelling the representation of a PR reviews config in a TOML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Right now is the same as UserConfig, but everything is optional
    skip_filenames: Optional[list[str]] = None
    skip_branches: Optional[set[str]] = None
    comments: Optional[CommentsTomlConfig] = None


class UserTomlConfig(UserConfig):
    """
    Internal class modelling the representation of a user config in a TOML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Right now is the same as UserConfig, but everything is optional
    pr_reviews: Optional[PRTomlConfig] = None
    check: Optional[CheckTomlConfig] = None


class _CommentsYamlConfig(CommentsConfig):
    """
    Internal class modelling the representation of a comments config in a YAML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Everything is optional
    taking_a_look: Optional[bool] = None
    no_findings: Optional[bool] = None


class _CheckYamlConfig(CheckConfig):
    """
    Internal class modelling the representation of a check config in a YAML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Everything is optional
    patterns: Optional[list[str]] = None
    exclude_patterns: Optional[list[str]] = None


class _PRYamlConfig(PRReviewsConfig):
    """
    Internal class modelling the representation of a PR reviews config in a YAML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Right now is the same as UserConfig, but everything is optional
    skip_filenames: Optional[list[str]] = None
    skip_branches: Optional[set[str]] = None
    comments: Optional[_CommentsYamlConfig] = None


class UserYamlConfig(UserConfig):
    """
    Internal class modelling the representation of a user config in a YAML file.
    """

    # Leave strict False so pydantic can cast from the parser types to this model types
    model_config = ConfigDict(strict=False, extra="allow")

    # Right now is the same as UserConfig, but everything is optional
    pr_reviews: Optional[_PRYamlConfig] = None
    check: Optional[_CheckYamlConfig] = None


try:
    # Make sure to update the corresponding user-facing documentation if this changes
    DEFAULT_PR_REVIEWS_CONFIG = PRReviewsConfig(
        skip_filenames=[
            "conda-lock.yml",
            "bun.lock",
            "go.mod",
            "requirements.txt",
            "uv.lock",
            ".terraform.lock.hcl",
            "Gemfile.lock",
            "package-lock.json",
            "yarn.lock",
            "composer.lock",
            "poetry.lock",
            "pdm.lock",
            "Cargo.lock",
            "go.sum",
            "Package.resolved",
            "Podfile.lock",
            "mix.lock",
            "*.ico",
            "*.jpeg",
            "*.jpg",
            "*.png",
            "*.svg",
        ],
        skip_branches=set(),
        comments=CommentsConfig(),
    )
except ValidationError as e:
    LOG.exception("Failed to create default PR reviews config.")
    raise e

try:
    DEFAULT_CONFIG = UserConfig(pr_reviews=DEFAULT_PR_REVIEWS_CONFIG)
except ValidationError as e:
    LOG.exception("Failed to create default user config.")
    raise e
