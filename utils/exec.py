import subprocess


def exec_command(command: str) -> bool:
    result = subprocess.Popen(
        command,
        shell=True,
    )
    result.wait()
    if result.returncode == 0:
        return True
    return False


def exec_command_return(command: str) -> str | bool:
    result = subprocess.Popen(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    result.wait()
    if result.returncode == 0:
        return result.stdout.read()
    return False
