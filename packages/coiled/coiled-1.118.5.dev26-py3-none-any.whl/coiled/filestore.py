from __future__ import annotations

import io
import os
import time
from pathlib import Path

import httpx
from rich.align import Align
from rich.console import Group
from rich.prompt import Confirm
from rich.status import Status

import coiled
from coiled.cli.curl import sync_request
from coiled.exceptions import CoiledException


def wait_until_complete(cluster_id, direction: str):
    done = False
    cluster_filestores = None
    timeout_at = time.monotonic() + 30
    while not done and time.monotonic() < timeout_at:
        cluster_filestores = FilestoreManager.get_cluster_filestores(cluster_id)
        if not cluster_filestores:
            return None
        cfs = cluster_filestores.get(direction, {})
        done = cfs.get("complete")
        if not done:
            time.sleep(2)
    return cluster_filestores


def download_from_filestore_with_ui(fs, into="."):
    if fs:
        # TODO (possible enhancement) if "has files" flag is set then make sure we do see files to download?
        blobs = FilestoreManager.get_download_list_with_urls(fs["id"])
        total_bytes = sum(blob["size"] for blob in blobs)

        size_label = "Bytes"
        size_scale = 1

        if total_bytes > 10_000_000:
            size_label = "Mb"
            size_scale = 1_000_000
        elif total_bytes > 10_000:
            size_label = "Kb"
            size_scale = 1_000

        def progress_title(f=None):
            return Group(
                Align.left(Status(f"Downloading from cloud storage: [green]{fs['name']}[green]", spinner="dots")),
                Align.left(f"Local directory: [green]{into}[/green]"),
                Align.left(f"Currently downloading: [blue]{f or ''}[/blue]"),
            )

        with coiled.utils.SimpleRichProgressPanel.from_defaults(title=progress_title()) as progress:
            done_files = 0
            done_bytes = 0

            progress.update_progress([
                {"label": "Files", "total": len(blobs), "completed": done_files},
                {
                    "label": size_label,
                    "total": total_bytes / size_scale if size_scale > 1 else total_bytes,
                    "completed": done_bytes / size_scale if size_scale > 1 else done_bytes,
                },
            ])

            for blob in blobs:
                progress.update_title(progress_title(blob["key"]))

                FilestoreManager.download_from_signed_url(
                    local_path=FilestoreManager.local_path_for_blob(fs_prefix=fs["prefix"], blob=blob, into=into),
                    url=blob["url"],
                )

                done_files += 1
                done_bytes += blob["size"]

                progress.update_progress([
                    {"label": "Files", "total": len(blobs), "completed": done_files},
                    {
                        "label": size_label,
                        "total": total_bytes / size_scale if size_scale > 1 else total_bytes,
                        "completed": done_bytes / size_scale if size_scale > 1 else done_bytes,
                    },
                ])

            progress.update_title(
                Group(
                    Align.left(f"Downloaded from cloud storage: [green]{fs['name']}[green]"),
                    Align.left(f"Local directory: [green]{into}[/green]"),
                )
            )


def upload_to_filestore_with_ui(fs, local_dir):
    FilestoreManager.post_fs_write_status(fs["id"], "start")

    def progress_title(f=None):
        return Group(
            Align.left(Status(f"Uploading to cloud storage: [green]{fs['name']}[green]", spinner="dots")),
            Align.left(f"Currently uploading: [blue]{f or ''}[/blue]"),
        )

    if fs and local_dir:
        files, total_bytes = FilestoreManager.get_files_for_upload(local_dir)

        size_label = "Bytes"
        size_scale = 1

        if total_bytes > 10_000_000:
            size_label = "Mb"
            size_scale = 1_000_000
        elif total_bytes > 10_000:
            size_label = "Kb"
            size_scale = 1_000

        with coiled.utils.SimpleRichProgressPanel.from_defaults(title=progress_title()) as progress:
            done_files = 0
            done_bytes = 0

            progress.update_progress([
                {"label": "Files", "total": len(files), "completed": done_files},
                {
                    "label": size_label,
                    "total": total_bytes / size_scale if size_scale > 1 else total_bytes,
                    "completed": done_bytes / size_scale if size_scale > 1 else done_bytes,
                },
            ])

            upload_urls = FilestoreManager.get_signed_upload_urls(fs["id"], files_for_upload=files)

            for local_path, relative_path, size in files:
                progress.batch_title = progress_title(local_path)
                progress.refresh()

                FilestoreManager.upload_to_signed_url(local_path, upload_urls[relative_path])

                done_files += 1
                done_bytes += size

                progress.update_progress([
                    {"label": "Files", "total": len(files), "completed": done_files},
                    {
                        "label": size_label,
                        "total": total_bytes / size_scale if size_scale > 1 else total_bytes,
                        "completed": done_bytes / size_scale if size_scale > 1 else done_bytes,
                    },
                ])

            progress.update_title(Align.left(f"Uploaded to cloud storage: [green]{fs['name']}[green]"))

        FilestoreManager.post_fs_write_status(fs["id"], "finish", {"complete": True, "file_count": len(files)})

        return len(files)


def clear_filestores_with_ui(cluster_filestores):
    # see if user wants to delete files from cloud storage now that job is done and results are downloaded
    if cluster_filestores.get("input").get("filestore"):
        # TODO (possible feature enhancement)
        #   distinguish filestores created for this specific job from "named" filestores made explicitly?
        coiled.filestore.clear_fs(fs=cluster_filestores["input"]["filestore"])
    if cluster_filestores.get("result").get("filestore"):
        coiled.filestore.clear_fs(fs=cluster_filestores.get("result").get("filestore"))


def clear_fs(fs):
    if fs:
        if Confirm.ask(f"Clear cloud storage for [green]{fs['name']}[/green]?", default=True):
            FilestoreManager.clear_fs(fs["id"])


class FilestoreManagerWithoutHttp:
    # code duplicated between coiled_agent.py and coiled client package
    http2 = False

    @staticmethod
    def make_req(api_path, post=False, data=None):
        raise NotImplementedError()

    @classmethod
    def create_filestores(cls, name, workspace, region):
        return cls.make_req(
            "/api/v2/filestore/pair", post=True, data={"name": name, "workspace": workspace, "region": region}
        )

    @classmethod
    def get_cluster_filestores(cls, cluster_id):
        return cls.make_req(f"/api/v2/filestore/cluster/{cluster_id}")

    @classmethod
    def get_signed_upload_urls(cls, fs_id, files_for_upload):
        paths = [p for _, p, _ in files_for_upload]  # relative paths
        return cls.make_req(f"/api/v2/filestore/fs/{fs_id}/signed-urls/upload", post=True, data={"paths": paths}).get(
            "urls"
        )

    @classmethod
    def get_download_list_with_urls(cls, fs_id):
        return cls.make_req(f"/api/v2/filestore/fs/{fs_id}/download-with-urls").get("blobs_with_urls")

    @classmethod
    def attach_filestores_to_cluster(cls, cluster_id, in_name, out_name):
        return cls.make_req(
            "/api/v2/filestore/attach",
            post=True,
            data={
                "cluster_id": cluster_id,
                "in_name": in_name,
                "out_name": out_name,
            },
        )

    @classmethod
    def post_fs_write_status(cls, fs_id, action: str, data: dict | None = None):
        # this endpoint uses cluster auth to determine the filestore
        cls.make_req(f"/api/v2/filestore/fs/{fs_id}/status/{action}", post=True, data=data)

    @classmethod
    def clear_fs(cls, fs_id):
        cls.make_req(f"/api/v2/filestore/fs/{fs_id}/clear", post=True)

    @staticmethod
    def get_files_for_upload(local_dir):
        files = []
        total_bytes = 0

        ignore_before_ts = 0
        if os.path.exists(os.path.join(local_dir, ".ignore-before")):
            ignore_before_ts = os.path.getmtime(os.path.join(local_dir, ".ignore-before"))

        for parent_dir, _, children in os.walk(local_dir):
            ignore_file_list = set()

            if ".ignore-list" in children:
                with open(os.path.join(parent_dir, ".ignore-list")) as f:
                    ignore_file_list = set(f.read().split("\n"))

            for child in children:
                local_path = os.path.join(parent_dir, child)

                # we use .ignore-before file so that if we're using a directory which already had files
                # (e.g., we're using same directory for inputs and outputs)
                # then we'll only upload new or modified files, not prior unmodified files
                if (
                    child.startswith(".ignore")
                    or child in ignore_file_list
                    or (ignore_before_ts and os.path.getmtime(local_path) < ignore_before_ts)
                ):
                    continue

                relative_path = Path(os.path.relpath(local_path, local_dir)).as_posix()
                size = os.path.getsize(local_path)

                files.append((local_path, relative_path, size))
                total_bytes += size
        return files, total_bytes

    @classmethod
    def upload_to_signed_url(cls, local_path, url):
        with open(local_path, "rb") as f:
            buffer = io.BytesIO(f.read())
            buffer.seek(0)
            num_bytes = len(buffer.getvalue())
            with httpx.Client(http2=cls.http2) as client:
                headers = {"Content-Type": "binary/octet-stream", "Content-Length": str(num_bytes)}
                if "blob.core.windows.net" in url:
                    headers["x-ms-blob-type"] = "BlockBlob"
                # TODO error handling
                client.put(
                    url,
                    # content must be set to an iterable of bytes, rather than a
                    # bytes object (like file.read()) because files >2GB need
                    # to be sent in chunks to avoid an OverflowError in the
                    # Python stdlib ssl module, and httpx will not chunk up a
                    # bytes object automatically.
                    content=buffer,
                    timeout=60,
                    headers=headers,
                )

    @classmethod
    def download_from_signed_url(cls, local_path, url):
        # TODO (performance enhancement) check if file already exists, skip if match, warn if not
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # TODO (performance enhancement) stream
        with httpx.Client(http2=cls.http2) as client:
            with open(local_path, "wb") as f:
                headers = {"Content-Type": "binary/octet-stream"}
                response = client.get(url, timeout=60, headers=headers)
                f.write(io.BytesIO(response.content).getbuffer())

    @staticmethod
    def local_path_for_blob(into, blob, fs_prefix):
        relative_path = blob["key"][len(fs_prefix) + 1 :]
        local_path = os.path.join(into, relative_path)
        return local_path


class FilestoreManager(FilestoreManagerWithoutHttp):
    http2 = True

    @staticmethod
    def make_req(api_path, post=False, data=None):
        workspace = (data or {}).get("workspace")
        with coiled.Cloud(workspace=workspace) as cloud:
            url = f"{cloud.server}{api_path}"
            response = sync_request(
                cloud=cloud,
                url=url,
                method="post" if post else "get",
                json=True,
                data=data,
                json_output=True,
            )
            if isinstance(response, dict) and response.get("error"):
                raise CoiledException(f"\n\n{response['error']}")
            return response
