import os
import sys
from tools.envgen.run_envgen import RunEnvGen
from tools.codegen.run_codegen import RunCodeGen
from tools.codetest.run_codetest import RunCodeTest


MODE_ENV_GEN = "gen"
MODE_CODE_GEN = "codegen"
MODE_TEST = "test"
MODE_USAGE = "usage"


def usage(args):
    print("[Usage]")
    print(f"{args[0]} gen   : to generate python workspace")
    print(f"{args[0]} test  : to test code in your python workspace")
    print(f"{args[0]} usage : show this tool's usage")


if __name__ == "__main__":

    cmdline_args = sys.argv

    if len(cmdline_args) < 2:
        usage(cmdline_args)
        sys.exit()

    root_dir = os.path.dirname(os.path.abspath(__file__))

    tool_prog = " ".join(cmdline_args[:2])
    tool_mode = cmdline_args[1]
    tool_args = cmdline_args[2:]

    if tool_mode == MODE_ENV_GEN:
        RunEnvGen(root_dir, tool_prog, tool_args).run()
    elif tool_mode == MODE_CODE_GEN:
        RunCodeGen(root_dir, tool_prog, tool_args).run()
    elif tool_mode == MODE_TEST:
        RunCodeTest(root_dir, tool_prog, tool_args).run()
    else:
        usage(cmdline_args)
