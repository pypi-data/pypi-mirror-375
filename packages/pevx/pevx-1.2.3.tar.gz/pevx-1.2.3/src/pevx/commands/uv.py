import os
import click
import subprocess

from pevx.utils import codeartifact

@click.command("uv", context_settings={"ignore_unknown_options": True})
@click.option('--domain', default='prudentia-sciences', show_default=True)
@click.option('--owner', default='545822668568', show_default=True)
@click.option('--region', default='us-east-1', show_default=True)
@click.option('--repo', default='pypi-store', show_default=True)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def uv_proxy(domain, owner, region, repo, args):
    """Proxy any uv command via CodeArtifact authentication.

    Example:
      pevx uv add requests
      pevx uv pip install -r requirements.txt
    """
    try:
        index_url = codeartifact.get_auth_url(domain=domain, owner=owner, region=region, repo=repo)
    except subprocess.CalledProcessError as e:
        raise click.ClickException(e.stderr)

    uv_cmd = ['uv'] + list(args)

    env = os.environ.copy()
    env['UV_EXTRA_INDEX_URL'] = index_url
    env['UV_INDEX_URL'] = 'https://pypi.org/simple/'

    github_env = env.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a') as fh:
            fh.write(f"UV_EXTRA_INDEX_URL={index_url}\n")
            fh.write(f"UV_INDEX_URL=https://pypi.org/simple/\n")

    subprocess.run(uv_cmd, check=True, env=env)
