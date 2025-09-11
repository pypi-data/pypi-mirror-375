import click

import coiled
from coiled.filestore import FilestoreManager, download_from_filestore_with_ui, upload_to_filestore_with_ui

from .cluster.utils import find_cluster
from .utils import CONTEXT_SETTINGS


@click.command(
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("cluster", default="", required=False)
@click.option(
    "--workspace",
    default=None,
    help="Coiled workspace (uses default workspace if not specified).",
)
@click.option("--into", default=".")
def download(cluster, workspace, into):
    with coiled.Cloud(workspace=workspace) as cloud:
        cluster_info = find_cluster(cloud, cluster)
        cluster_id = cluster_info["id"]
        fs = FilestoreManager.get_cluster_filestores(cluster_id).get("download", {}).get("filestore")
    if not fs:
        print(f"No filestore found for {cluster_info['name']} ({cluster_info['id']})")
    download_from_filestore_with_ui(fs, into)


@click.command(
    context_settings=CONTEXT_SETTINGS,
)
@click.argument("cluster", default="", required=False)
@click.option(
    "--workspace",
    default=None,
    help="Coiled workspace (uses default workspace if not specified).",
)
@click.option("--from", "local_dir", required=True)
def upload(cluster, workspace, local_dir):
    with coiled.Cloud(workspace=workspace) as cloud:
        cluster_info = find_cluster(cloud, cluster)
        cluster_id = cluster_info["id"]
        fs = FilestoreManager.get_cluster_filestores(cluster_id).get("upload", {}).get("filestore")
    if not fs:
        print(f"No filestore found for {cluster_info['name']} ({cluster_info['id']})")
    upload_to_filestore_with_ui(fs, local_dir)


@click.group(name="file", context_settings=CONTEXT_SETTINGS)
def file_group(): ...


file_group.add_command(download)
file_group.add_command(upload)
