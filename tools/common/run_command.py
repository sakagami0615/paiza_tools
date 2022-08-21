import subprocess
from typing import List, Tuple


def run_command(
    exec_cmd: List[str], input_file_path: Tuple[int, str]
) -> Tuple[int, str]:
    with open(input_file_path, "r", encoding="utf-8") as f:
        proc = subprocess.run(
            exec_cmd,
            stdin=f,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        actual = proc.stdout[:-1]  # 末尾の改行を1文字削除
    return proc.returncode, actual
