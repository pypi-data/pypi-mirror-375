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

    secret_path = Path(f"/run/secrets/{secret_id}")
    aws_dir = Path("/root/.aws")
    root_cred_path = aws_dir / "credentials"
    tmp_backup_path = Path("/tmp/.aws/credentials.bak")

    created_root_dir = False
    wrote_new_creds = False
    backed_up_existing = False

    try:
        if is_github and secret_path.exists():
            if not aws_dir.exists():
                aws_dir.mkdir(parents=True, exist_ok=True)
                created_root_dir = True

            if root_cred_path.exists():
                tmp_backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root_cred_path, tmp_backup_path)
                backed_up_existing = True

            shutil.copy2(secret_path, root_cred_path)
            wrote_new_creds = True

        # Make sure AWS knows where to look
        env["AWS_SHARED_CREDENTIALS_FILE"] = str(root_cred_path)
        env.setdefault("AWS_REGION", region)

        # Fetch CodeArtifact index URL
        try:
            index_url = codeartifact.get_auth_url(domain=domain, owner=owner, region=region, repo=repo)
        except subprocess.CalledProcessError as e:
            msg = (e.stderr.decode() if isinstance(e.stderr, bytes | bytearray) else e.stderr) or str(e)
            raise click.ClickException(msg)

        # Build the uv command
        uv_cmd = ["uv"] + list(args)

        # Point uv/pip at CodeArtifact + PyPI
        env["UV_EXTRA_INDEX_URL"] = index_url
        env["UV_INDEX_URL"] = "https://pypi.org/simple/"

        # Persist for later GitHub steps if applicable
        if is_github and github_env:
            with open(github_env, "a") as fh:
                fh.write(f"UV_EXTRA_INDEX_URL={index_url}\n")
                fh.write("UV_INDEX_URL=https://pypi.org/simple/\n")
                fh.write(f"AWS_SHARED_CREDENTIALS_FILE={root_cred_path}\n")
                fh.write(f"AWS_REGION={region}\n")

        # Run the command
        subprocess.run(uv_cmd, check=True, env=env)

    finally:
        # Restore/cleanup credentials if we wrote new ones from the secret
        if is_github:
            if wrote_new_creds and root_cred_path.exists():
                root_cred_path.unlink(missing_ok=True)
            if backed_up_existing and tmp_backup_path.exists():
                tmp_backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tmp_backup_path, root_cred_path)
                tmp_backup_path.unlink(missing_ok=True)
            # If we created the .aws dir only for this run and it’s now empty, remove it
            if created_root_dir and aws_dir.exists():
                try:
                    aws_dir.rmdir()
                except OSError:
                    pass
