from vyomcloudbridge.constants import install_type

class InstallationInfo:
    @property
    def installation_type(self) -> str:
        return install_type.INSTALLATION_TYPE

    @property
    def is_lite_installation(self) -> bool:
        return self.installation_type == "lite"

    @property
    def is_full_installation(self) -> bool:
        return self.installation_type == "full"
