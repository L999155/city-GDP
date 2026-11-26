#!/usr/bin/env python3
"""把 data.json / industry.json 注入 template.html，生成单文件站点 index.html。

用法：
    python build.py
"""

import json
import os
import pathlib
import shutil
import sys

BASE = pathlib.Path(__file__).resolve().parent
# 可选的产业结构数据来源：环境变量或同目录 industry.json
INDUSTRY_SRC = pathlib.Path(
    os.environ.get("INDUSTRY_JSON", str(BASE / "industry.json"))
)


def main() -> int:
    data_path = BASE / "data.json"
    tpl_path = BASE / "template.html"
    out_path = BASE / "index.html"

    if not data_path.exists() or not tpl_path.exists():
        print("缺少 data.json 或 template.html", file=sys.stderr)
        return 1

    raw = data_path.read_text(encoding="utf-8")
    regions = json.loads(raw)
    payload = raw.replace("</", "<\\/")

    # 产业结构数据：默认同目录 industry.json，可用 INDUSTRY_JSON 指定其它来源
    ind_local = BASE / "industry.json"
    if INDUSTRY_SRC.exists() and INDUSTRY_SRC.resolve() != ind_local.resolve():
        if not ind_local.exists() or INDUSTRY_SRC.stat().st_mtime > ind_local.stat().st_mtime:
            shutil.copyfile(INDUSTRY_SRC, ind_local)
    if ind_local.exists():
        ind_raw = ind_local.read_text(encoding="utf-8")
        industry = json.loads(ind_raw)
        ind_payload = ind_raw.replace("</", "<\\/")
    else:
        industry = {}
        ind_payload = "{}"
        print("警告：未找到 industry.json，产业结构数据为空", file=sys.stderr)

    tpl = tpl_path.read_text(encoding="utf-8")
    if "__DATA__" not in tpl:
        print("template.html 中缺少 __DATA__ 占位符", file=sys.stderr)
        return 1
    if "__INDUSTRY__" not in tpl:
        print("template.html 中缺少 __INDUSTRY__ 占位符", file=sys.stderr)
        return 1

    py_path = BASE / "pinyin.json"
    if py_path.exists():
        py_raw = py_path.read_text(encoding="utf-8")
        py_payload = py_raw.replace("</", "<\\/")
    else:
        py_payload = "{}"
        print("警告：未找到 pinyin.json，拼音搜索不可用", file=sys.stderr)

    map_path = BASE / "map_paths.json"
    if map_path.exists():
        mp_raw = map_path.read_text(encoding="utf-8")
        mp = json.loads(mp_raw)
        main = mp["main"]; ins = mp["inset"]
        map_payload = mp_raw.replace("</", "<\\/")
        vb_main = "%s %s %s %s" % (main["x"], main["y"], main["w"], main["h"])
        vb_inset = "%s %s %s %s" % (ins["x"], ins["y"], ins["w"], ins["h"])
    else:
        map_payload = '{"shapes":[],"jd":""}'
        vb_main = vb_inset = "0 0 1000 750"
        print("警告：未找到 map_paths.json，概览地图为空", file=sys.stderr)

    html = (tpl.replace("__VB_MAIN__", vb_main)
               .replace("__VB_INSET__", vb_inset)
               .replace("__MAPDATA__", map_payload)
               .replace("__DATA__", payload)
               .replace("__INDUSTRY__", ind_payload)
               .replace("__PINYIN__", py_payload))
    out_path.write_text(html, encoding="utf-8", newline="\n")
    print(
        "index.html 已生成：{:,} 字节，{} 个地区，{} 个产业结构对象".format(
            len(html.encode("utf-8")), len(regions), len(industry)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
