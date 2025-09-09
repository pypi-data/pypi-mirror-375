import logging

import typer
from typer import prompt

from pae_toolkit.util.logging_util import setup_logging

setup_logging(level=logging.INFO)

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    pretty_exceptions_short=False,
)


@app.command(help="检查 MindIE 高性能所需环境变量配置")
def mindie_precheck(
    cmd: str = typer.Option(""),
) -> None:
    from pae_toolkit.mindie.check_env import check

    check.show_suggest()


@app.command(help="MindIE 性能测试")
def mindie_preformance() -> None:
    print(
        "cd /usr/local/Ascend/atb-models/tests/modeltest/ && bash run.sh pa_bf16 performance [[1024,20]] 1 1 qwen /data/weights/ 2"
    )


@app.command(help="ONNX 模型简化")
def onnx_sim(onnx_path: str = "/home/allm/pae-toolkit/.asset/yolov10n.onnx") -> None:
    from pae_toolkit.onnx.onnx_sim import simplify_onnx

    simplify_onnx(onnx_path)


@app.command(help="ViT模型改图优化")
def vit_optimize(onnx_path: str, save_path: str, model_config: str):
    from pae_toolkit.onnx.optimize_vit import apply_optimization

    apply_optimization(onnx_path, save_path, model_config)


@app.command(help="[废弃] 启动单机PD服务")
def start_single_machine_pd_server(
    start_npu_id: int = typer.Option(-1),
    p_node_num: int = typer.Option(-1),
    npu_num_per_p_node: int = typer.Option(-1),
    d_node_num: int = typer.Option(-1),
    npu_num_per_d_node: int = typer.Option(-1),
    docker_image: str = typer.Option(""),
    model_path: str = typer.Option(""),
):
    from pae_toolkit.pd import Config, start_pd

    config = Config()
    config.start_npu_id = int(prompt("起始的NPU ID")) if start_npu_id < 0 else start_npu_id
    config.p_node_num = int(prompt("P节点数量")) if p_node_num < 0 else p_node_num
    config.npu_num_per_p_node = int(prompt("每个P节点NPU数量")) if npu_num_per_p_node < 0 else npu_num_per_p_node
    config.d_node_num = int(prompt("D节点数量")) if d_node_num < 0 else d_node_num
    config.npu_num_per_d_node = int(prompt("每个D节点NPU数量")) if npu_num_per_d_node < 0 else npu_num_per_d_node
    config.docker_image = str(prompt("Docker镜像")) if docker_image == "" else docker_image
    config.model_path = str(prompt("模型路径")) if model_path == "" else model_path
    return start_pd(config)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
