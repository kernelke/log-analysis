import os
import sys
import subprocess
import ctypes
import winreg
from pathlib import Path


def check_admin():
    """检查管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_install_path(executable):
    """从注册表查找软件安装路径"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{executable}")
        path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        return Path(path)
    except:
        return None


def check_dependencies():
    """检查必要依赖"""
    # 检查Node.js
    node_path = get_install_path("node.exe") or get_install_path("nodejs.exe")
    if not node_path or not (node_path.parent / "npm.cmd").exists():
        print("❌ 未检测到Node.js，请访问 https://nodejs.org/ 下载安装")
        return False

    # 检查Python
    python_path = get_install_path("python.exe") or Path(sys.executable)
    if not python_path.exists():
        print("❌ 未检测到Python，请访问 https://www.python.org/ 下载安装")
        return False

    return True


def install_deps():
    """安装项目依赖"""
    print("\n🔧 安装Python依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print("\n🛠️ 安装前端依赖...")
    os.chdir("frontend")
    subprocess.run(["npm.cmd", "install", "--no-optional"], check=True)
    os.chdir("..")


def start_services():
    """启动服务"""
    # 启动后端
    backend_proc = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    # 启动前端
    os.chdir("frontend")
    subprocess.run(["npm.cmd", "start"], check=True)
    os.chdir("..")

    backend_proc.terminate()


def main():
    if not check_admin():
        print("请以管理员权限运行此脚本！")
        input("按回车键退出...")
        return

    print("""
    ░█████╗░██╗░░░░░██╗░░░██╗███╗░░██╗██╗░░██╗
    ██╔══██╗██║░░░░░██║░░░██║████╗░██║██║░██╔╝
    ██║░░╚═╝██║░░░░░██║░░░██║██╔██╗██║█████═╝░
    ██║░░██╗██║░░░░░██║░░░██║██║╚████║██╔═██╗░
    ╚█████╔╝███████╗╚██████╔╝██║░╚███║██║░╚██╗
    ░╚════╝░╚══════╝░╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝
    """)

    if not check_dependencies():
        input("按回车键退出...")
        return

    try:
        install_deps()
        start_services()
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行出错: {e}")
    except KeyboardInterrupt:
        print("\n操作已取消")
    finally:
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()