import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import click

BASE_URL = "https://api.github.com/repos/pyaether/altar-ui/releases/latest"


def get_latest_release_tag() -> str | None:
    try:
        request = Request(  # noqa: S310
            BASE_URL,
            headers={
                "User-Agent": "aether-pyaltar-cli",
                "Accept": "application/vnd.github.v3+json",
            },
        )  # noqa: S310
        with urlopen(request) as response:  # noqa: S310
            if response.status != 200:
                raise click.ClickException(
                    f"GitHub API request failed with status code: {response.status}"
                )
            latest_release_dict = json.loads(response.read().decode("utf-8"))
            return latest_release_dict["tag_name"]
    except HTTPError as error:
        raise click.ClickException(
            f"GitHub API request failed with status code: {error.code}"
        )
    except URLError as error:
        raise click.ClickException(f"Failed to reach GitHub API: {error.reason}")
    except json.JSONDecodeError as error:
        raise click.ClickException(
            f"Failed to parse JSON response from GitHub API: {error}"
        )
    except Exception as error:
        raise click.ClickException(
            f"Unexpected error fetching latest release version: {error}"
        )


def parse_version_slug(slug: str) -> str:
    refs, version = slug.split("@", maxsplit=1)

    if not refs or refs in ["release", "tag"]:
        refs = "tags"
    elif refs == "branch":
        refs = "heads"
    else:
        raise click.BadArgumentUsage(f"Invalid specifier: {refs}.")

    match version:
        case "latest":
            latest_version = get_latest_release_tag()
            parsed_slug = f"{refs}/{latest_version}"
        case _:
            if re.match(r"^v\d+\.\d+\.\d+$", version):
                parsed_slug = f"{refs}/{version}"
            else:
                parsed_slug = f"{refs}/{version}"

    return parsed_slug
