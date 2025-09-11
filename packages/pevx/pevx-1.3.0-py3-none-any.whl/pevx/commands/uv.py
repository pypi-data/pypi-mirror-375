import os
import shutil
import subprocess
from pathlib import Path

import click

from pevx.utils import codeartifact


@click.command("uv", context_settings={"ignore_unknown_options": True})
@click.option("--secret-id", default="aws_credentials", show_default=True)
@click.option("--domain", default="prudentia-sciences", show_default=True)
@click.option("--owner", default="545822668568", show_default=True)
@click.option("--region", default="us-east-1", show_default=True)
@click.option("--repo", default="pypi-store", show_default=True)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def uv_proxy(secret_id, domain, owner, region, repo, args):
    """Proxy any uv command via CodeArtifact authentication.

    Example:
      pevx uv add requests
      pevx uv pip install -r requirements.txt
    """
    env = os.environ.copy()
    github_env = env.get("GITHUB_ENV")
    is_github = bool(github_env)

    if is_github:
        secret_path = Path(f"/run/secrets/{secret_id}")
        if secret_path.exists():
            root_cred_path = Path("/root/.aws/credentials")
            if root_cred_path.exists():
                tmp_cred_path = Path("/tmp/.aws/credentials")
                tmp_cred_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(root_cred_path, tmp_cred_path, dirs_exist_ok=True)
            else:
                root_cred_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copytree(secret_path, root_cred_path, dirs_exist_ok=True)

    try:
        index_url = codeartifact.get_auth_url(domain=domain, owner=owner, region=region, repo=repo)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(e.stderr)

    uv_cmd = ["uv"] + list(args)

    env["UV_EXTRA_INDEX_URL"] = index_url
    env["UV_INDEX_URL"] = "https://pypi.org/simple/"

    if is_github:
        with open(github_env, "a") as fh:
            fh.write(f"UV_EXTRA_INDEX_URL={index_url}\n")
            fh.write("UV_INDEX_URL=https://pypi.org/simple/\n")

    subprocess.run(uv_cmd, check=True, env=env)

    if is_github and secret_path.exists():
        shutil.rmtree(root_cred_path)
        if tmp_cred_path and tmp_cred_path.exists():
            shutil.copytree(root_cred_path, tmp_cred_path, dirs_exist_ok=True)
            shutil.rmtree(tmp_cred_path)
