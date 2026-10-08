"""Deployment ASGI entrypoint with operational routes installed."""

from deepresearch.api import create_app
from deepresearch.ops.readiness import install_readiness

app = create_app()
install_readiness(app)
