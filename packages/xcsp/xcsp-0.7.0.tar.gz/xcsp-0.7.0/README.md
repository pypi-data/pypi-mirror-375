# XCSP-Launcher

[![License: LGPL v3+](https://img.shields.io/badge/License-LGPL%20v3%2B-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Documentation](https://app.readthedocs.org/projects/xcsp/badge/?version=latest)](https://xcsp-doc.tootatis.dev)
[![Python Tests](https://github.com/CPToolset/XCSP-Launcher/actions/workflows/tests.yml/badge.svg)](https://github.com/CPToolset/XCSP-Launcher/actions/workflows/tests.yml)
[![Release](https://github.com/CPToolset/XCSP-Launcher/actions/workflows/release.yml/badge.svg)](https://github.com/CPToolset/XCSP-Launcher/actions/workflows/release.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=CPToolset_XCSP-Launcher&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=CPToolset_XCSP-Launcher)


---

**XCSP-Launcher** is a unified tool to **install**, **build**, and **execute** solvers supporting the [XCSP3](http://xcsp.org/) format.

It provides a streamlined way to manage solvers, automate their compilation, and run constraint programming instances through a standard, extensible interface.

---

## ✨ Features

- 🛠️ **Solver installation** from GitHub, GitLab, or custom URLs
- 🧱 **Automatic or manual build** (Gradle, CMake, Makefile, Cargo, Maven, etc.)
- 🔖 **Solver versioning** and multi-version management
- ⚡ **Unified execution interface** for solving XCSP3 instances
- 📝 **Support for solver configuration files** (`.xsc.yaml`) for reproducibility
- 📄 **Detailed logging** of build and run processes
- 🧩 **Extensible**: Easily add support for new solvers

---

## 📦 Installation

You can install `xcsp-launcher` via PyPI:

```bash
pip install xcsp
```

Or from source:

```bash
git clone https://github.com/CPToolset/xcsp-launcher.git
cd xcsp-launcher
pip install .
```


<details>
<summary>Debian/Ubuntu</summary>

Download the latest binary from [github releases](https://github.com/CPToolset/XCSP-Launcher/releases/) and run:

```bash
sudo dpkg -i xcsp-launcher*.deb
```
</details>

<details>
<summary>MacOS</summary>

Install via [Homebrew](https://brew.sh):

```bash
brew tap CPToolset/homebrew-xcsp-launcher
brew install xcsp
```
</details>


---

## 🚀 Quick Start

### Install a solver

```bash
xcsp install --id ace --name ACE --repo xcsp3team/ace --source github.com
```

This will:
- Clone the solver repository,
- Automatically detect the build system (or use configuration),
- Build the solver,
- Register it in your local solver repository.

---

### Solve an instance

```bash
xcsp solve --solver ace --instance path/to/instance.xml
```

---

## 🧰 Example Configuration (.xsc.yaml)

```yaml
name: "ACE"
id: "fr.cril.xcsp.ace"
git: "https://github.com/xcsp3team/ace"
language: "java"
build:
  mode: manual
  build_command: "gradle build -x test"
command:
  prefix: "java -jar"
  template: "{{executable}} {{instance}} {{options}}"
  always_include_options: "-npc=true -ev"
versions:
  - version: "2.4"
    git_tag: "2.4"
    executable: "build/lib/ACE-2.4.jar"
```

For more information about the format of the solver-configuration please see the documentation of [`metrics`](https://github.com/crillab/metrics-solvers/blob/main/format.md).  

---

## 🛠 Supported Build Systems (Auto-detection)

- Gradle (`build.gradle`)
- Maven (`pom.xml`)
- CMake (`CMakeLists.txt`)
- Make (`Makefile`)
- Rust Cargo (`Cargo.toml`)
- Python setuptools (`setup.py`, `pyproject.toml`)

---

## 📚 Other Projects

- [`xcsp-launcher-homebrew`](https://github.com/CPToolset/xcsp-launcher-homebrew) — Homebrew Tap for installing XCSP-Launcher easily on macOS/Linux.
- [`xcsp-metadata`](https://github.com/CPToolset/xcsp-metadata) — A metadata repository for XCSP3 instances (domains, categories, etc.).
- [`metrics-solver`](https://github.com/crillab/metrics-solvers) — Predefined solver configurations available by default with `xcsp-launcher` for easy installation and experimentation.

---

## 🚀 Projects Using XCSP-Launcher

- [`metrics`](https://github.com/crillab/metrics) — An open-source Python library to automate experimental campaigns and analyze solver performances.

---

## 🤝 Contributing

We welcome contributions!  
Feel free to open issues, suggest features, or submit pull requests.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## ⚖️ License

This project is licensed under the **LGPL v3+** License.  
See [LICENSE](LICENSE) for details.

---

## 🌍 Related Links

- [XCSP3 Official Website](http://xcsp.org/)
- [PyCSP3 Python Modeling Library](http://pycsp.org/)

---