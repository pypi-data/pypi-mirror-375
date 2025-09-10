import sys
import ctypes
import subprocess
from pyautogui import alert


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def disable_googleupdater_services_sc():
    # 获取所有服务信息
    output = subprocess.check_output(["sc", "query", "type=", "service", "state=", "all"], text=True, encoding='gbk')
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SERVICE_NAME:"):
            svc = line.split(":", 1)[1].strip()
            if svc.startswith("GoogleUpdater") or svc in ['gupdate', 'gupdatem']:
                subprocess.run(["sc", "config", svc, "start=", "disabled"], check=False)
                subprocess.run(["sc", "stop", svc], check=False)


if __name__ == "__main__":
    if not is_admin():
        # 用runas启动当前Python脚本，弹出UAC提升提示
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join(['"%s"' % arg for arg in sys.argv]), None, 1
        )
    disable_googleupdater_services_sc()
    alert('chrome自动更新已禁用。请在浏览器设置->关于chrome检验。')
