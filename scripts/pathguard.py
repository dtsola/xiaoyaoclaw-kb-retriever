#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pathguard.py — 写盘路径的容器校验（防符号链接越界写入）

语言 / Language：注释与报错默认中文；**语言可选**，按用户语言回应即可
（comments default to Chinese; error text can be adapted to the user's language）。

为什么需要它：知识库目录里可能存在**符号链接**（用户自己建的、同步盘建的、
或从压缩包解出来的）。只做字符串层面的校验（`abspath` + `commonpath` /
`startswith`）**看不出链接**：`<kb>/sub -> /etc` 这样的链接会让一个"看起来在
库内"的路径实际写到库外。本模块是三个写盘脚本共用的唯一闸门。

规则
  1. 先把知识库根解析成**真实路径**（`realpath`，解开沿途所有符号链接）。
  2. 每个写入目标同样解析成真实路径（已存在的部分解链，尚未存在的尾段原样保留）
     —— 这个真实路径必须仍落在库根内部，否则拒绝。
  3. 目标已存在且是符号链接时同上：解出来的真实路径越界即拒绝（不会"跟着链接"写出去）。
  4. **fail closed**：任何校验不通过都直接报错退出，绝不"先写再说"。

不做：不删除任何文件；不跟随链接到库外（既不写、也不在库外建目录）。
"""

from __future__ import annotations

import os
import sys


class PathEscapeError(RuntimeError):
    """写入目标解析后越出知识库根（通常是符号链接导致的）。"""


def _norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


def real_root(path: str) -> str:
    """把知识库根解析成真实路径（必须是已存在的目录）。"""
    p = os.path.realpath(os.path.expanduser(str(path)))
    if not os.path.isdir(p):
        raise PathEscapeError(f"知识库根目录不存在或不是目录：{p}")
    return p


def real_target(path: str) -> str:
    """把待写目标解析成真实路径（解掉已存在部分的符号链接）。"""
    return os.path.realpath(os.path.expanduser(str(path)))


def is_within(root_real: str, target_real: str, *, allow_equal: bool = False) -> bool:
    """target 是否在 root 内部（或等于 root，且显式允许）。大小写按平台归一。"""
    r, t = _norm(root_real), _norm(target_real)
    if t == r:
        return allow_equal
    return t.startswith(r.rstrip(os.sep) + os.sep)


def assert_within(root_real: str, target: str, *, what: str = "写入目标") -> str:
    """校验 target（含符号链接解析）必须落在 root_real 内，返回真实路径。"""
    resolved = real_target(target)
    if not is_within(root_real, resolved):
        raise PathEscapeError(
            f"{what}解析后越出知识库根（符号链接或异常路径），已拒绝：{target} -> {resolved}"
        )
    return resolved


def check_or_exit(root: str, target: str, *, what: str = "写入目标") -> str:
    """CLI 入口用：校验失败即打印错误并以退出码 2 结束（fail closed）。"""
    try:
        return assert_within(real_root(root), target, what=what)
    except PathEscapeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


def is_symlink(path: str) -> bool:
    """目标本身是否为符号链接（用于显式披露/拒绝）。"""
    return os.path.islink(os.path.expanduser(str(path)))
