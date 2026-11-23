"""Fail closed before loading the recorded chess harness."""
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["MSWEA_GLOBAL_CONFIG_DIR"] = str(ROOT / ".offline_settings")


def deny_network(*args, **kwargs):
    raise RuntimeError("Network prohibited during M3 offline preparation")


# Kept so that an explicitly authorized live stage can undo the block.
REAL_CONNECT = socket.socket.connect
REAL_CREATE_CONNECTION = socket.create_connection
socket.socket.connect = deny_network
socket.create_connection = deny_network
sys.path[:0] = [str(ROOT), str(ROOT / "vendor/pr917")]
import caaf_agent as agent
import caaf_chess as chess_env

agent.CaafModel.query = deny_network
chess_env._TB_DIR = ROOT / "inputs/tablebases"
OUT = ROOT / "experiments/m3_offline_v1"
