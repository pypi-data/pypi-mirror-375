import sys, os ,socket
import logging
from pathlib import Path

from . import run_app
from . import callpatch
import anvil_app_server as server
import pyargman

logger = logging.getLogger(__name__)
original_argv = sys.argv.copy()

def get_free_port():
    "for navil server runtime. for finding unused port to bind.so coexist with another anvil apps"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # 0 tells OS to pick an available port
        return s.getsockname()[1]

class aviyal:
    """
    this is for running anvil_runtime programically instead comandline.
    it is internally using comandline java comand to run a jar file that exist in anvi folder
    """

    def __init__(self, app_path, ANVIL_DESKTOP_DEPENDECYS = None ,port = None ):
        # sys.executable = None  # if we set this then anvil server script wil change it and it will cause error

        self.app_path = self._get_app_path( app_path )
        self.ANVIL_DESKTOP_DEPENDECYS = ANVIL_DESKTOP_DEPENDECYS
        self.java_path = str ( self.ANVIL_DESKTOP_DEPENDECYS / Path("jre/bin") ) if ANVIL_DESKTOP_DEPENDECYS else Path(__file__)  # os.path.abspath(os.path.join(self.base_folder, "jre/bin"))
        self.argman = pyargman.ArgManager("test")
        self.argman.set_arg("--app", self.app_path)
        self.port = port if port else get_free_port()
        self.argman.set_arg("--port", self.port)
        self.set_config_if_exists()

    def set_config_if_exists(self):
        "anvil server parameters canbe writen to a file then pass its path as argument."
        config_path = self.app_path / Path("config.yaml")
        if config_path.resolve().exists(): #if main app needs app depemndencys then it should exist
            logger.info(f"config file found {config_path}")
            self.argman.set_arg("--config-file", config_path )

    def get_arguemnts(self):
        return self.argman.tolist() + original_argv[1:]

    def _get_app_path(self, appname):
        if not os.path.isabs(appname):
            app_path = Path(appname).resolve()
        else:
            app_path = appname
        return app_path

    @staticmethod
    def set_env_var(path):
        os.environ["PATH"] = f"{path}" + os.pathsep + os.environ["PATH"]
        logger.info(f" added java jre path to enviornment varibale = {path}")

    def set_config(self):
        sys.argv = self.get_arguemnts()
        self.set_env_var(self.java_path)
        # anvil server will call jaav.so to stop raising errors this path must available

    def run(self):

        if len(sys.argv) > 1:
            logger.info(" running as proxy to python.exe, because some arguments provided while starting")
            logger.info(f" passed arguments {sys.argv}")
            try:
                run_app.main()
            except Exception as error:
                logger.warning(" while running as proxy it raised an error maybe input script contain errors ", error)
        else:
            self.set_config()
            logger.info(f" launching embedded jar because this exe is started without any arguments ")
            logger.info(f" passed arguments {sys.argv}")
            with callpatch.SubprocessCallPatcher( ):
                server.launch()


def set_cert():
    "without this the  automatic server jar file downlaoding fail with SSL error in windows 10 vm"
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()


set_cert()  # must be called before calling anvil

if __name__ == "__main__":

    try:
        ANVIL_APP_FOLDER_NAME = Path("ANVIL_APPS/MyTodoList")
        app_path = f"{ANVIL_APP_FOLDER_NAME}"
        stub_path = Path("ANVIL_DESKTOP_DEPENDENCYS")
        logger.info("anvil_desktop path working folder is ", app_path)
        anvilobj = aviyal(app_path, ANVIL_DESKTOP_DEPENDECYS = stub_path)
        anvilobj.run()
    except Exception as e:
        print(" #### ERROR in aviyal desktop  execution =", e)
