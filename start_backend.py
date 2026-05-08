#!/usr/bin/env python3
"""一键启动 Django 后端。

默认端口：127.0.0.1:18001
用法：
  python3 start_backend.py
  python3 start_backend.py --restart
  python3 start_backend.py --host 0.0.0.0 --port 18001

行为：
  - 端口未占用：执行迁移并以前台方式启动 Django，持续打印 runserver 日志。
  - 后端已运行：默认不退出，进入健康检查监听；使用 --restart 可重启后由脚本接管并打印 Django 实时日志。
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
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


def dashboard_ok(host: str, port: int) -> tuple[bool, str]:
    try:
        with urlopen(f"http://{host}:{port}/api/dashboard/", timeout=2) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status == 200, body
    except URLError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)


def run(command: list[str]) -> None:
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def find_port_pids(port: int) -> list[str]:
    try:
        result = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def stop_port(port: int) -> None:
    pids = find_port_pids(port)
    if not pids:
        return
    print(f"停止占用 {port} 端口的进程：{', '.join(pids)}", flush=True)
    subprocess.run(["kill", *pids], cwd=ROOT, check=False)
    for _ in range(20):
        if not find_port_pids(port):
            return
        time.sleep(0.2)
    remaining = find_port_pids(port)
    if remaining:
        print(f"进程未退出，强制停止：{', '.join(remaining)}", flush=True)
        subprocess.run(["kill", "-9", *remaining], cwd=ROOT, check=False)


def monitor_existing(host: str, port: int, interval: int) -> int:
    url = f"http://{host}:{port}"
    print(f"后端已经在运行：{url}", flush=True)
    print(f"健康检查：{url}/api/dashboard/", flush=True)
    print("进入监听模式；按 Ctrl+C 退出此窗口，不会停止已存在的后端进程。", flush=True)
    print("如果要查看 Django runserver 实时请求日志，请执行：python3 start_backend.py --restart", flush=True)

    try:
        while True:
            ok, body = dashboard_ok(host, port)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            status = "OK" if ok else "ERROR"
            print(f"[{timestamp}] backend {status} {url}/api/dashboard/ {body[:200]}", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n已退出监听模式", flush=True)
        return 0


def start_backend(host: str, port: int, skip_sync: bool, skip_migrate: bool) -> int:
    url = f"http://{host}:{port}"
    try:
        if not skip_sync:
            run(["uv", "sync"])
        if not skip_migrate:
            run(["uv", "run", "python", "manage.py", "migrate", "--noinput"])
        print(f"启动后端：{url}", flush=True)
        print("Django 日志会持续打印在这里；按 Ctrl+C 停止后端。", flush=True)
        subprocess.run(
            ["uv", "run", "python", "manage.py", "runserver", f"{host}:{port}"],
            cwd=ROOT,
            check=True,
        )
    except KeyboardInterrupt:
        print("\n后端已停止", flush=True)
        return 0
    except FileNotFoundError as exc:
        print(f"缺少命令：{exc.filename}。请先安装 uv。", flush=True)
        return 1
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="一键启动 TRON Django 后端")
    parser.add_argument("--host", default=os.getenv("BACKEND_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("BACKEND_PORT", DEFAULT_PORT)))
    parser.add_argument("--skip-sync", action="store_true", help="跳过 uv sync")
    parser.add_argument("--skip-migrate", action="store_true", help="跳过数据库迁移")
    parser.add_argument("--restart", action="store_true", help="如果端口已有后端在运行，先停止再以前台方式启动，方便查看实时日志")
    parser.add_argument("--monitor-interval", type=int, default=10, help="后端已运行时的健康检查间隔秒数")
    args = parser.parse_args()

    if port_is_open(args.host, args.port):
        ok, _body = dashboard_ok(args.host, args.port)
        if args.restart:
            stop_port(args.port)
        elif ok:
            return monitor_existing(args.host, args.port, max(1, args.monitor_interval))
        else:
            print(f"端口 {args.port} 已被占用，但健康检查不是当前 Django 后端。", flush=True)
            print(f"如确认可以重启该端口，请执行：python3 start_backend.py --restart --port {args.port}", flush=True)
            return 1

    return start_backend(args.host, args.port, args.skip_sync, args.skip_migrate)


if __name__ == "__main__":
    raise SystemExit(main())
