# setup.py
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


default_requirements = [
    "argparse",
    # Add any other dependencies your package needs
]

try:
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file) as f:
            requirements = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    else:
        print("requirements.txt not found, using default requirements")
        requirements = default_requirements
except Exception as e:
    print(f"Error reading requirements.txt, using default requirements: {e}")
    requirements = default_requirements

setup(
    name="vyomcloudbridge",
    version="0.2.81", # for non - ros
    cmdclass={
        'install': CustomInstallCommand,
    },
    packages=find_packages(exclude=["tests", "tests.*", "extra", "extra.*"]),
    install_requires=requirements,
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
    include_package_data=True
    # This puts install_script.sh in the data directory
    # data_files=[
    #     ("share/vyomcloudbridge", ["install_script.sh"]),
    # ],
    # # This installs install_script.sh as a script in the bin directory
    # scripts=["install_script.sh"],
)
