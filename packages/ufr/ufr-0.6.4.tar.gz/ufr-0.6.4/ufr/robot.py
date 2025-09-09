import os
import sh
from pathlib import Path
# from virtualenv import cli_run




class Robot:
    def __init__(self, path="./build"):
        self.dir = { "bin": {}, "proc":{}, "data": {}}
        self.root = Path(path).absolute()

        # self.venv = cli_run(["robot.d"])
        sh.mkdir("-p", self.root)

        os.environ['VIRTUAL_ENV'] = str(self.root)
        os.environ['PATH'] = f"{self.root}/bin:{os.environ['PATH']}"
        os.environ['PYTHONPATH'] = f"{self.root}/bin"
        os.environ['PIP_REQUIRE_VIRTUALENV'] = 'true'
        os.environ['LD_LIBRARY_PATH'] = f"{self.root}/lib:/usr/local/webots/lib/controller/"
        os.system("hash -r")

    def install_source(self, path: str):
        repo_path = Path(path).absolute()
        name = repo_path.stem

        build_path = self.root / "tmp" / name 
        sh.mkdir("-p", build_path)
        os.system(f"cd '{build_path}'; cmake -DCMAKE_INSTALL_PREFIX='{self.root}' '{repo_path}'; make; make install")

    def install_repository(self, url: str):
        name = Path(url).stem
        repo_path = self.root / "src" / name        
        if not repo_path.exists():
            sh.git.clone(url, repo_path)

        build_path = self.root / "tmp" / name 
        sh.mkdir("-p", build_path)
        print(f"cd '{build_path}'; cmake -DCMAKE_INSTALL_PREFIX='{self.root}' '{repo_path}'; make; make install")
        os.system(f"cd '{build_path}'; cmake -DCMAKE_INSTALL_PREFIX='{self.root}' '{repo_path}'; make; make install")

    def pip_install(self, package_name: str):
        res = sh.pip3("install", package_name)
        print(res)

    def start(self, command_name: str):
        os.system(f"{command_name} &")

    def make_topic(self, name, text):
        self.dir['data'][name] = text
        os.environ[f"LT_SYS_{name}"] = text


    def cmd_ls(self):
        for key,val in self.dir.items():
            print(key)

    def generate_bash_source(self):
        text = f"export PATH={os.environ['PATH']}\n"
        text += f"export LD_LIBRARY_PATH={os.environ['LD_LIBRARY_PATH']}\n\n"
        for topic_name, topic_val in self.dir['data'].items():
            text += f"export UFR_SYS_{topic_name}='{topic_val}'\n"
        fd = open( str(self.root/"setup.bash"), "w" )
        fd.write(text)
        fd.close()

    def shell(self):
        pwd = Path("/")
        pwd_stack = [self.dir]
        print("Robot 1 ###")
        while True:
            line_ = input(f"root:{pwd}# ").split(' ')
            cmd_ = line_[0]
            if cmd_ == 'ls':
                self.cmd_ls()
            elif cmd_ == 'cd':
                name = line_[1]
                if name == '..':
                    pwd_stack.pop(0)
                else:
                    if name in pwd_stack[-1]:
                        pwd_stack.append(pwd_stack[-1][name])
                        pwd = pwd / name
            elif cmd_ == 'exit':
                break
