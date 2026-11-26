#!/usr/bin/env python3
"""把 data.json 注入 template.html，生成单文件站点 index.html。

用法：
    python build.py
"""

import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent


def main() -> int:
    data_path = BASE / "data.json"
    tpl_path = BASE / "template.html"
    out_path = BASE / "index.html"

    if not data_path.exists() or not tpl_path.exists():
        print("缺少 data.json 或 template.html", file=sys.stderr)
        return 1

    raw = data_path.read_text(encoding="utf-8")
    regions = json.loads(raw)
    # 避免数据中出现 </script> 截断内联脚本
    payload = raw.replace("</", "<\\/")

    tpl = tpl_path.read_text(encoding="utf-8")
    if "__DATA__" not in tpl:
        print("template.html 中缺少 __DATA__ 占位符", file=sys.stderr)
        return 1

    html = tpl.replace("__DATA__", payload)
    out_path.write_text(html, encoding="utf-8", newline="\n")
    print(
        "index.html 已生成：{:,} 字节，{} 个地区".format(
            len(html.encode("utf-8")), len(regions)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
