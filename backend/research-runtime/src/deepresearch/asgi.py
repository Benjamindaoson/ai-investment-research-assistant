"""Deployment ASGI entrypoint with operational routes installed."""

from deepresearch.api import create_app
from deepresearch.ops.access_control import install_access_control
from deepresearch.ops.audit import install_audit_log
from deepresearch.ops.http_boundary import install_http_boundary
from deepresearch.ops.readiness import install_readiness

app = create_app()
install_http_boundary(app)
install_readiness(app)
install_access_control(app)
install_audit_log(app)
