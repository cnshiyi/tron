#!/usr/bin/env python3
"""一键启动 Django 后端。

默认端口：127.0.0.1:18001
用法：
  python3 start_backend.py
  python3 start_backend.py --host 0.0.0.0 --port 18001
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 18001


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def dashboard_ok(host: str, port: int) -> bool:
    try:
        with urlopen(f"http://{host}:{port}/api/dashboard/", timeout=2) as response:
            return response.status == 200
    except URLError:
        return False
    except Exception:
        return False


def run(command: list[str]) -> None:
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="一键启动 TRON Django 后端")
    parser.add_argument("--host", default=os.getenv("BACKEND_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("BACKEND_PORT", DEFAULT_PORT)))
    parser.add_argument("--skip-sync", action="store_true", help="跳过 uv sync")
    parser.add_argument("--skip-migrate", action="store_true", help="跳过数据库迁移")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    if port_is_open(args.host, args.port):
        if dashboard_ok(args.host, args.port):
            print(f"后端已经在运行：{url}")
            print(f"健康检查：{url}/api/dashboard/")
            return 0
        print(f"端口 {args.port} 已被占用，但不是当前 Django 后端。请先关闭占用进程。")
        return 1

    try:
        if not args.skip_sync:
            run(["uv", "sync"])
        if not args.skip_migrate:
            run(["uv", "run", "python", "manage.py", "migrate", "--noinput"])
        print(f"启动后端：{url}", flush=True)
        subprocess.run(
            ["uv", "run", "python", "manage.py", "runserver", f"{args.host}:{args.port}"],
            cwd=ROOT,
            check=True,
        )
    except KeyboardInterrupt:
        print("\n后端已停止")
        return 0
    except FileNotFoundError as exc:
        print(f"缺少命令：{exc.filename}。请先安装 uv。")
        return 1
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
