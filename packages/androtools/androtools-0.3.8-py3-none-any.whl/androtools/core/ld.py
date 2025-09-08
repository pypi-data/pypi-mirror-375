# 雷电模拟器
import shutil
from time import sleep

import psutil

from androtools.android_sdk import CMD
from androtools.core.device import Device, DeviceInfo
from androtools import logger


class LDConsole(CMD):
    """使用 ldconsole.exe 对模拟器进行管理"""

    def __init__(self, path=shutil.which("ldconsole.exe")):
        super().__init__(path)

    def list_devices(self):
        """列出所有模拟器信息

        0. 索引
        1. 标题
        2. 顶层窗口句柄
        3. 绑定窗口句柄
        4. 运行状态, 0-停止,1-运行,2-挂起
        5. 进程ID, 不运行则为 -1.
        6. VBox进程PID
        7. 分辨率-宽
        8. 分辨率-高
        9. dpi

        Returns:
            _type_: _description_
        """
        return self._run(["list2"])

    def launch_device(self, idx: int | str):
        return self._run(["launch", "--index", str(idx)])

    def is_running(self, idx: int | str):
        r, _ = self._run(["isrunning", "--index", str(idx)])
        return r == "running"

    def getprop(self, idx: int | str, prop: str | None = None) -> str:
        if prop:
            out, _ = self._run(["getprop", "--index", str(idx), "--key", prop])
        else:
            out, _ = self._run(["getprop", "--index", str(idx)])
        return out.strip()

    # setprop <--name mnq_name | --index mnq_idx> --key <name> --value <val>
    def setprop(self, idx: int | str, prop: str, val: str):
        return self._run(
            ["setprop", "--index", str(idx), "--key", prop, "--value", val]
        )

    # installapp <--name mnq_name | --index mnq_idx> --filename <apk_file_name>
    def install_app(self, idx: int | str, apk_path: str):
        return self._run(["installapp", "--index", str(idx), "--filename", apk_path])

    # uninstallapp <--name mnq_name | --index mnq_idx> --packagename <apk_package_name>
    def uninstall_app(self, idx: int | str, package_name: str):
        return self._run(
            ["uninstallapp", "--index", str(idx), "--packagename", package_name]
        )

    # runapp <--name mnq_name | --index mnq_idx> --packagename <apk_package_name>
    def run_app(self, idx: int | str, package_name: str):
        return self._run(["runapp", "--index", str(idx), "--packagename", package_name])

    # killapp <--name mnq_name | --index mnq_idx> --packagename <apk_package_name>
    def kill_app(self, idx: int | str, package_name: str):
        return self._run(
            ["killapp", "--index", str(idx), "--packagename", package_name]
        )

    # locate <--name mnq_name | --index mnq_idx> --LLI <Lng,Lat>
    def locate(self, idx: int | str, lng: float, lat: float):
        return self._run(["locate", "--index", str(idx), "--LLI", f"{lng},{lat}"])

    def reboot_device(self, idx: int | str):
        return self._run(["reboot", "--index", str(idx)])

    def quit_device(self, idx: int | str):
        return self._run(["quit", "--index", str(idx)])

    def quit_all_devices(self):
        return self._run(["quit-all"])

    def adb(self, idx, cmd: str | list, encoding: str | None = None):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        cmd = ["adb", "--index", str(idx), "--command", cmd]
        return self._run(cmd, encoding=encoding)

    def adb_shell(self, idx, cmd: str, encoding: str | None = None):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        return self.adb(idx, f"shell {cmd}", encoding=encoding)


def find_adb():
    for process in psutil.process_iter():
        if process.name() == "adb.exe":
            return True
    return False


class LDPlayer(Device):
    """雷电模拟器"""

    def __init__(self, info: DeviceInfo) -> None:
        super().__init__(info)
        self.index = info.index
        self.name = info.name
        self.ldconsole = LDConsole(info.console_path)

    def kill_app(self, package):
        self.ldconsole.kill_app(self.index, package)

    def is_boot(self):
        return self.ldconsole.is_running(self.index)

    def is_crashed(self):
        """
        判断模拟器是否没响应，如果没响应，则定义为模拟器崩溃
        需要判断设备崩溃吗？
        """
        # NOTE - 注意：每个模拟器的情况不一样！

        # 启动 com.android.settings
        self.adb_shell(["am", "start", "com.android.settings"])
        sleep(3)
        # dumpsys window windows | grep mCurrentFocus
        out, _ = self.adb_shell(
            ["dumpsys", "window", "windows", "|", "grep", "mCurrentFocus"]
        )
        if "com.android.settings" not in out:
            logger.warning(f"[{self.name}] 无法启动设置，杀死系统界面，重新启动设置。")
            self.kill_app("com.android.launcher3")
            self.adb_shell(["am", "start", "com.android.settings"])
            out, _ = self.adb_shell(
                ["dumpsys", "window", "windows", "|", "grep", "mCurrentFocus"]
            )
            if "com.android.settings" not in out:
                logger.warning(f"[{self.name}] 无法启动设置，可能需要重启模拟器。")
                return True

        self.home()
        out, _ = self.adb_shell(
            ["dumpsys", "window", "windows", "|", "grep", "mCurrentFocus"]
        )
        if "com.android.launcher3" not in out:
            logger.warning(f"[{self.name}] 回到桌面失败，请检查模拟器是否正常启动。")
            return True
        return False

    def launch(self):
        if self.is_boot():
            return
        self.ldconsole.launch_device(self.info.index)

    def getprop(self, prop: str | None = None):
        return self.ldconsole.getprop(self.index, prop)

    def install_app(self, apk_path: str):
        r = self.ldconsole.install_app(self.index, apk_path)
        return True, str(r[0] + r[1])

    def uninstall_app(self, package_name: str):
        self.ldconsole.uninstall_app(self.index, package_name)

    def run_app(self, package):
        self.ldconsole.run_app(self.index, package)
        return True

    def close(self):
        self.ldconsole.quit_device(self.index)

    def reboot(self):
        self.ldconsole.reboot_device(self.index)
        return self.get_status()

    def adb_by_console(self, cmd: str | list, encoding: str | None = None):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        return self.ldconsole.adb(self.index, cmd, encoding=encoding)

    def adb_shell_by_console(self, cmd: str | list, encoding: str | None = None):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        return self.ldconsole.adb_shell(self.index, cmd, encoding=encoding)
