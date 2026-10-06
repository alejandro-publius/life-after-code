"""Deployment placeholder. Claude replaces this with the chosen FastAPI app."""
import os

from fastapi import FastAPI

app = FastAPI(title="Life After Code deployment placeholder")


@app.get("/healthz")
def healthz():
    return {"ok": True, "commit": os.environ.get("CI_COMMIT_SHORT_SHA") or "local"}
