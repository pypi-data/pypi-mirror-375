import os
import re
from typing import Optional
from fastmcp import Client as FastMCPClient
import boto3


class ZmpKnowledgeStoreClient(FastMCPClient):
    """
    MCP client for ZMP Knowledge Store, aligned with FastMCP best practices.
    Usage:
        async with ZmpKnowledgeStoreClient(api_url) as client:
            result = await client.call_tool("ingest_documents", {"documents": payload})
    """

    def __init__(self, api_url):
        super().__init__(api_url)


# Load from environment variables, fallback to defaults
API_URL = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:5371/mcp")
BASE_DOC_URL = os.environ.get("BASE_DOC_URL", "http://docs.cloudzcp.net")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "zmp-ai-knowledge-store")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-2")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def upload_image_to_s3(local_path, s3_filename):
    s3_key = f"assets/{s3_filename}"
    s3_client.upload_file(
        local_path, S3_BUCKET_NAME, s3_key, ExtraArgs={"ContentType": "image/png"}
    )
    return s3_key


async def ingest_documents_for_job(
    job_docs_dir: str,
    job_img_dir: str,
    solution: str,
    doc_url: Optional[str] = None,
    export_path: Optional[str] = None,
):
    """
    Ingest MDX documents and their assets from the job-specific directory or a single file to the MCP server.
    If export_path is a file, ingest only that file and its images.
    If export_path is a directory, ingest all .mdx files in that directory and subdirectories.
    """
    api_url = API_URL
    documents = []

    files_to_ingest = []
    if export_path:
        export_path_abs = os.path.abspath(export_path)
        if os.path.isfile(export_path_abs):
            files_to_ingest = [export_path_abs]
        elif os.path.isdir(export_path_abs):
            for root, _, files in os.walk(export_path_abs):
                for file in files:
                    if file.endswith(".mdx"):
                        files_to_ingest.append(os.path.join(root, file))
    else:
        job_docs_dir_abs = os.path.abspath(job_docs_dir)
        for root, _, files in os.walk(job_docs_dir_abs):
            for file in files:
                if file.endswith(".mdx"):
                    files_to_ingest.append(os.path.join(root, file))

    for mdx_path in files_to_ingest:
        with open(mdx_path, "r", encoding="utf-8") as f:
            content = f.read()
        asset_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
        assets = []
        for asset_path in asset_refs:
            img_prefix = f"img/{solution.lower()}/"
            if asset_path.startswith("/" + img_prefix):
                asset_rel_path = asset_path[len("/" + img_prefix) :]
            elif asset_path.startswith(img_prefix):
                asset_rel_path = asset_path[len(img_prefix) :]
            else:
                asset_rel_path = asset_path.lstrip("/")
            abs_asset_path = os.path.join(job_img_dir, asset_rel_path)
            if not os.path.exists(abs_asset_path):
                abs_asset_path = os.path.join(os.path.dirname(mdx_path), asset_path)
            print(f"[Ingest] Checking asset: {asset_path} -> {abs_asset_path}")
            if os.path.exists(abs_asset_path):
                s3_key = upload_image_to_s3(
                    abs_asset_path, os.path.basename(asset_path)
                )
                assets.append(
                    {
                        "filename": os.path.basename(asset_path),
                        "assets_s3_keys": [s3_key],
                    }
                )
            else:
                print(f"[Ingest] Asset not found: {abs_asset_path}")
        job_docs_dir_abs = os.path.abspath(job_docs_dir)
        # Change the mdx_path to the path under the job specific directory if needed
        if not os.path.abspath(mdx_path).startswith(job_docs_dir_abs):
            # Compute the relative path from the repo root, then join to job_docs_dir_abs
            rel_from_repo = os.path.relpath(
                mdx_path, os.environ.get("REPO_ROOT", os.getcwd())
            )
            mdx_path = os.path.join(job_docs_dir_abs, rel_from_repo)

        rel_path = os.path.relpath(mdx_path, job_docs_dir_abs)
        # Remove 'repo/docs/{solution}/' from the start of rel_path if present
        prefix = f"repo/docs/{solution.lower()}/"
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix) :]
        rel_url_path = os.path.splitext(rel_path)[0]
        rel_url_path = rel_url_path.replace(os.sep, "/")
        # Always compute doc_url per document
        full_doc_url = f"{BASE_DOC_URL}/{solution}/{rel_url_path}"
        documents.append(
            {
                "filename": rel_path,
                "content": content,
                "content_type": "text/mdx",
                "assets": assets,
                "solution": solution,
                "doc_url": full_doc_url,
            }
        )
    print(f"[Ingest] {mdx_path} refers to images: {asset_refs}")

    async with ZmpKnowledgeStoreClient(api_url) as client:
        result = await client.call_tool(
            "ingest_documents",
            {"documents": documents, "solution": solution},
        )
        print(f"[Ingest] Result: {result}")
        return result
