"""Deployment ASGI entrypoint with operational routes installed."""

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.ops.readiness import install_readiness

app = create_app()
install_readiness(app)
install_access_control(app)
