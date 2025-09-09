import logging
import os
import platform
import shlex
import subprocess
from dataclasses import dataclass
from typing import Callable

from rich import print as rprint

from pae_toolkit.util.logging_util import outpath


def red(text:str):
    return f'[red]{text}[/red]'

def green(text:str):
    return f'[green]{text}[/green]'


def shell(cmd:str):
    return subprocess.run(shlex.split(cmd), capture_output=True).stdout.decode()

@dataclass
class Suggest:
    desc:str
    cmd:str
    enabled:bool

class Check_Performance:
    def __init__(self)->None:
        self.suggetions:list[Suggest] = []
        self.suggetion_str = "#!/bin/bash\n"

    def add_suggest(self, desc:str, cmd:str):
        def decorated(f) -> Callable:
            ret = f()

            cmd_str = ""
            if len(cmd.split("\n")) > 1:
                cmd_str = "\n".join([ii.strip() for ii in cmd.split("\n")])
            else:
                cmd_str = f'{cmd.strip()}\n'
            self.suggetion_str += cmd_str
            self.suggetions.append(Suggest(desc=desc, cmd=cmd, enabled=ret))
            return ret
        return decorated

    def show_suggest(self) ->None:
        for i in self.suggetions:
            flag = red("[X]")

            if i.enabled:
                logging.debug(f'{i.cmd}, {i.cmd}')
                continue

            if len(i.cmd.split("\n")) > 1:
                exports = [z.strip() for z in i.cmd.split("\n") if z.strip() !='']
                for j in exports:
                    rprint(f'{flag}',end=' ')
                    print(j)
            else:
                rprint(f'{flag}',end=' ')
                print(i.cmd)
            if i.desc.strip() !='':
                print(f'\t{i.desc}')
        if not all([i.enabled  for i in self.suggetions]):
            save_env_file = outpath / "toolkit_set_env.sh"
            with open(save_env_file, 'w', encoding='utf-8') as f:
                print(self.suggetion_str, file=f)
                rprint(f'{green("[Tip]")} env saved to {save_env_file}, source {save_env_file} to enable.')
        else:
            rprint('Success set_env.')
check = Check_Performance()


@check.add_suggest(
    desc=f"""CPU高性能模式{
    {
        "操作系统名称及版本号": platform.platform(),
        "Python版本": platform.python_version(),
        "CPU核数": str(os.cpu_count()),
    }
}""",
    cmd="""
    # CPU 高性能模式
    cpupower -c all frequency-set -g performance
    """,
)
def check_machine() ->bool:
    res = shell("cpupower frequency-info |grep performance")
    return res != ""


@check.add_suggest(
    desc="expect OMP_NUM_THREADS in [1,10]",
    cmd="""
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
    """
)
def check_omp() -> bool:
    return all([
        os.getenv("OMP_PROC_BIND") == "false",
        0 < int(os.getenv("OMP_NUM_THREADS", 0)) <= 10
    ])

@check.add_suggest(desc="开启透明大页",cmd="echo always > /sys/kernel/mm/transparent_hugepage/enabled", )
def check_hugepage() -> bool:
    check = "cat /sys/kernel/mm/transparent_hugepage/enabled"
    if platform.system() == "Linux":
        logging.debug(check)
        cmd_res = shell(check)
        if cmd_res.split()[0] != "[always]":
            rprint("[red]Transparent Hugepages is disabled[/red]")

    return shell(check) == ""

@check.add_suggest(
    desc="0: no affinity, 1: cpu affinity, 2: cpu affinity + numa ,粗粒度绑核，与taskset冲突",
    cmd="export CPU_AFFINITY_CONF=2"
)
def check_bind_cpu() -> bool:
    # os.environ["CPU_AFFINITY_CONF"]="2"
    return os.getenv("CPU_AFFINITY_CONF") == "2"


@check.add_suggest(
    desc="下发队列优化",
    cmd="export TASK_QUEUE_ENABLE=2"
)
def check_task() -> bool:
    return os.getenv("TASK_QUEUE_ENABLE") == "2"

@check.add_suggest(
    desc="""[通过此环境变量可控制缓存分配器行为。](https://www.hiascend.com/document/detail/zh/Pytorch/710/comref/Envvariables/Envir_012.html)""",
    cmd="export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True",
)
def check_pytorch() ->bool:
    return os.getenv("PYTORCH_NPU_ALLOC_CONF") == "expandable_segments:True"


@check.add_suggest(
    desc="""""",
    cmd="""
    export HCCL_OP_EXPANSION_MODE=AIV
    export HCCL_DETERMINISTIC=false # # 关闭确定性计算
    """,
)
def check_hccl() ->bool:
    return all([
        os.getenv("HCCL_OP_EXPANSION_MODE") == "AIV",
        os.getenv("HCCL_DETERMINISTIC")=="false"
        ])

@check.add_suggest(
    desc="""非阻塞模式""",
    cmd="""
    export ASCEND_LAUNCH_BLOCKING=""
    """,
)
def check_blocking() ->bool:
    return all([
        os.getenv("ASCEND_LAUNCH_BLOCKING") == "",
        ])

@check.add_suggest(
    desc="""
    日志等级:
    0：对应DEBUG级别。
    1：对应INFO级别。
    2：对应WARNING级别。
    3：对应ERROR级别，默认为ERROR级别。
    4：对应NULL级别，不输出日志。
    """,
    cmd="""
    export ASCEND_GLOBAL_LOG_LEVEL=3
    """,
)
def check_mindie_loglevel() ->bool:
    return os.getenv("ASCEND_GLOBAL_LOG_LEVEL") in ['','4','3']

@check.add_suggest(
    desc="""区间:(0.94, 0.99)""",
    cmd="""
    export NPU_MEMORY_FRACTION=0.95
    """,
)
def check_npu_mem() ->bool:
    return 0.94<= float(os.getenv("NPU_MEMORY_FRACTION", 0.8)) <=0.99


@check.add_suggest(
    desc=""" """,
    cmd="""
    export INF_NAN_MODE_FORCE_DISABLE=1
    """,
)
def check_inf() ->bool:
    return os.getenv("INF_NAN_MODE_FORCE_DISABLE") == "1"

@check.add_suggest(
    desc='',
    cmd="""
export MINDIE_LOG_TO_STDOUT="0"
export MINDIE_LOG_TO_FILE="0"
export MINDIE_LOG_LEVEL="error"
export MINDIE_ASYNC_SCHEDULING_ENABLE="1"
export ATB_LLM_HCCL_ENABLE="1"
export ATB_LLM_COMM_BACKEND="hccl"
export ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE="3"
export ATB_WORKSPACE_MEM_ALLOC_GLOBAL="1"
export ATB_LLM_ENABLE_AUTO_TRANSPOSE="0"
export ATB_LAYER_INTERNAL_TENSOR_REUSE="1"
export ATB_OPERATION_EXECUTE_ASYNC="1"
export ATB_CONVERT_NCHW_TO_ND="1"
export ATB_CONTEXT_WORKSPACE_SIZE="0"
export ATB_LAUNCH_KERNEL_WITH_TILING="1"
""",
)
def check_mindie() ->bool:
    return all(
        [
            os.getenv("MINDIE_LOG_TO_FILE")=="0",
            os.getenv("MINDIE_LOG_TO_STDOUT")=="0",
            os.getenv("MINDIE_LOG_LEVEL")=="error",
            os.getenv("MINDIE_ASYNC_SCHEDULING_ENABLE")=="1",
            os.getenv("ATB_LLM_HCCL_ENABLE")=="1",
            os.getenv("ATB_LLM_COMM_BACKEND")=="hccl",
            os.getenv("ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE")=="3",
            os.getenv("ATB_WORKSPACE_MEM_ALLOC_GLOBAL")=="1",
            os.getenv("ATB_LLM_ENABLE_AUTO_TRANSPOSE")=="0",
            os.getenv("ATB_LAYER_INTERNAL_TENSOR_REUSE")=="1",
            os.getenv("ATB_OPERATION_EXECUTE_ASYNC")=="1",
            os.getenv("ATB_CONVERT_NCHW_TO_ND")=="1",
            os.getenv("ATB_CONTEXT_WORKSPACE_SIZE")=="0",
            os.getenv("ATB_LAUNCH_KERNEL_WITH_TILING")=="1",
        ]
    )
