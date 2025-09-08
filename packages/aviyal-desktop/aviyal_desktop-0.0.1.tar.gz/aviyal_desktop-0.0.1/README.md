### aviyal_desktop_library

An unofficial tool for running Anvil apps locally in a desktop environment.  
This library allows you to programmatically run the Anvil runtime, internally using a Java command to run a JAR file bundled with your Anvil app. It is especially useful for embedding Anvil-based web apps into a desktop setting or automating local Anvil app launches.

#### Features

- Programmatic interface (`aviyal` class) to run Anvil apps without using the command line.
- Mimics Python executable behavior for running scripts and modules, useful for PyInstaller-based desktop apps.
- Automatically manages Java runtime environment and port configuration.
- Supports passing configuration files and managing app dependencies.
- Handles SSL certificate setup for server JAR downloads (critical for Windows environments).

#### Installation

Clone the repository and include it in your Python environment:

```sh
git clone https://github.com/its-me-abi/aviyal_desktop_library.git
cd aviyal_desktop_library
# install dependencies as needed
```

#### Usage

Here is an example of starting an Anvil server locally with an app created using the online Anvil editor:

```python
from aviyal_desktop.aviyal_desktop import aviyal
from pathlib import Path

app_path = Path("ANVIL_APPS/MyTodoList")
stub_path = Path("ANVIL_DESKTOP_DEPENDENCYS")
anvilobj = aviyal(app_path, ANVIL_DESKTOP_DEPENDECYS=stub_path)
anvilobj.run()
```

- `app_path`: Path to your exported Anvil app.
- `ANVIL_DESKTOP_DEPENDECYS`: Path to the directory containing dependencies (e.g., Java Runtime).

#### How it works

- The `aviyal` class assembles command-line arguments, manages dependencies, and launches the Anvil server.
- If a `config.yaml` file is present in the app directory, it will be used for additional server configuration.
- The library sets up the environment so that embedded Java and Python executables work seamlessly for both direct launching and proxy execution.

#### License
This software is distributed under the GNU Affero General Public License v3 (AGPLv3), with a special exception for Anvil applications. See the [LICENSE](LICENSE) file for details.

#### credits
all credits goes to creators of anvil system.because this tool is created on top of it
