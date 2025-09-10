from pathlib import Path
import setuptools
from setuptools.command.build import build
import subprocess
import os


class CustomBuild(build):
    """
    Custom build that ensures the frontend assets are built before the Python package is built.

    The GH workflow we use for publishing python packages requires using `poetry build` to build the package.
    So we customize the build steps here to include building the frontend code so it can be included
    in the python package
    """

    def run(self):
        print("Custom build command running...")
        self.build_frontend()
        build.run(self)

    def build_frontend(self):
        """Build frontend assets, but skip if dist artifacts already exist (e.g., from sdist).

        In CI (source tree), we build via Yarn. In PEP 517 wheel-from-sdist builds, the dist
        directories are already present; we should not re-run JS builds there.
        """
        cwd = Path(__file__).parent.joinpath("streamlit_tetrascience_ui/components")
        packages_dir = cwd / "packages"
        dist_paths = [
            packages_dir / "streamlit-component-lib" / "dist",
            packages_dir / "ui" / "dist",
            packages_dir / "frontend" / "dist",
        ]
        # If all required dist directories exist and are non-empty, skip rebuilding
        if all(p.exists() and any(p.rglob("*")) for p in dist_paths):
            print("Frontend dist assets already present; skipping build.")
            return

        # Otherwise, perform per-package builds
        build_order = ["streamlit-component-lib", "ui", "frontend"]
        if cwd.joinpath("package.json").exists():
            subprocess.run(["bash", "-lc", "yarn install"], check=True, cwd=cwd)
        for name in build_order:
            pkg_path = packages_dir / name
            if pkg_path.exists() and pkg_path.joinpath("package.json").exists():
                subprocess.run(
                    ["bash", "-lc", f"yarn --cwd {pkg_path} install"],
                    check=True,
                    cwd=cwd,
                )
                subprocess.run(
                    ["bash", "-lc", f"yarn --cwd {pkg_path} run build"],
                    check=True,
                    cwd=cwd,
                )
        print("Frontend assets built (per-package builds).")


with open("README.md", "r") as fh:
    long_description = fh.read()

version_from_env = os.environ.get("TSPKG_VERSION", "0.1.5")

setuptools.setup(
    name="tetrascience-streamlit-ui",
    version=version_from_env,
    author="TetraScience",
    description="Use Tetrascience UI components in Streamlit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tetrascience/ts-lib-ui-kit-streamlit",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.9",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    cmdclass={
        "build": CustomBuild,
    },
    # extras_require={
    #     "devel": [
    #         "wheel",
    #         "pytest==7.4.0",
    #         "playwright==1.36.0",
    #         "requests==2.31.0",
    #         "pytest-playwright-snapshot==1.0",
    #         "pytest-rerunfailures==12.0",
    #     ]
    # }
)
