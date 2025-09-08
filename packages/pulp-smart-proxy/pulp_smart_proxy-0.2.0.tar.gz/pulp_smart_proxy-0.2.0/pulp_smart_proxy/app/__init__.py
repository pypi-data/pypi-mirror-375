from pulpcore.plugin import PulpPluginAppConfig


class PulpSmartProxyPluginAppConfig(PulpPluginAppConfig):
    """Entry point for the smart_proxy plugin."""

    name = "pulp_smart_proxy.app"
    label = "smart_proxy"
    version = "0.2.0"
    python_package_name = "pulp_smart_proxy"
    domain_compatible = True
