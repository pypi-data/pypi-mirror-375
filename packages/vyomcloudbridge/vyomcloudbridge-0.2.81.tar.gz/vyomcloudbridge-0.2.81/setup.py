from setuptools import setup, find_packages
import os
from setuptools.command.install import install


class CustomInstallCommand(install):
    def run(self):
        # default is full
        install_type = "full"

        # pip sets self.distribution.extras when extras are requested
        extras = getattr(self.distribution, "extras", [])
        if "lite" in extras:
            install_type = "lite"

        # write marker file
        constants_dir = os.path.join(
            os.path.dirname(__file__), "vyomcloudbridge", "constants"
        )
        os.makedirs(constants_dir, exist_ok=True)
        with open(os.path.join(constants_dir, "install_type.py"), "w") as f:
            f.write(f'INSTALLATION_TYPE = "{install_type}"\n')

        print(f"[vyomcloudbridge] Installed as {install_type}")
        super().run()


# Define base requirements (including pymavlink by default)
base_requirements = [
    "paho-mqtt",
    "awsiotsdk>=1.22.1",
    "build>=1.2.2.post1",
    "cv-bridge>=1.13.0.post0",
    "empy==3.3.4",
    "numpy>=1.24.3,<2.0",
    "opencv-python>=4.11.0.86,<4.12",
    "paho-mqtt==2.1.0",
    "pika>=1.3.2",
    "psutil>=5.9.0",
    "requests>=2.32.3",
    "twine>=6.1.0",
    "pymavlink>=2.4.47",  # Include by default
]

# Lite requirements (without pymavlink)
lite_requirements = [
    "paho-mqtt",
    "awsiotsdk>=1.22.1",
    "build>=1.2.2.post1",
    "cv-bridge>=1.13.0.post0",
    "empy==3.3.4",
    "numpy>=1.24.3,<2.0",
    "opencv-python>=4.11.0.86,<4.12",
    "paho-mqtt==2.1.0",
    "pika>=1.3.2",
    "psutil>=5.9.0",
    "requests>=2.32.3",
    "twine>=6.1.0",
]

# Detect if lite is being installed
import sys

requirements = base_requirements
if "--extra" in " ".join(sys.argv) and "lite" in " ".join(sys.argv):
    requirements = lite_requirements

# Define extras
extras_require = {
    "lite": [],  # Lite mode uses different base requirements
    "full": [],  # Full mode uses default base requirements
}

setup(
    name="vyomcloudbridge",
    version="0.2.81",
    cmdclass={
        "install": CustomInstallCommand,
    },
    packages=find_packages(exclude=["tests", "tests.*", "extra", "extra.*"]),
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "vyomcloudbridge=vyomcloudbridge.cli:main",
        ],
    },
    author="Vyom OS Admin",
    author_email="admin@vyomos.org",
    description="A communication service for vyom cloud",
    python_requires=">=3.6",
    package_data={"vyomcloudbridge": ["scripts/*.sh"]},
    include_package_data=True,
)
