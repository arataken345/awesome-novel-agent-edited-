#!/usr/bin/env python3
"""tools/prose_global_rules.py 回归测试：跨语言全局硬规则一致性。

覆盖 check-prose.py（中文）与 check-prose-en.py（英文）共用的确定性规则：
冒号/分号禁令（含全角：；）、一段一对话单元（含 CJK 引号）、em dash 仅警告、
prose-only 屏蔽（YAML/代码/URL/HTML 注释），以及 em-dash corpus 工具冒烟测试。

用法: python tools/test_prose_global_rules.py
返回码 0 = 全部通过。
"""
import contextlib
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_util import check, summary, exit_code, load_module

TOOLS = Path(__file__).resolve().parent
GR = load_module("prose_global_rules", TOOLS / "prose_global_rules.py")
CHECK_EN = load_module("check_prose_en_gr", TOOLS / "check-prose-en.py")
CHECK_CN = load_module("check_prose_gr", TOOLS / "check-prose.py")
CORPUS = load_module("check_emdash_corpus", TOOLS / "check-emdash-corpus.py")


def en_failures(text, **kwargs):
    return CHECK_EN.check_text(text, **kwargs).failures


def en_warnings(text, **kwargs):
    return CHECK_EN.check_text(text, **kwargs).warnings


def run_cn(text):
    """写临时文件跑 check-prose.py main()，返回 (退出码, stdout)。"""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(text)
        path = f.name
    argv_backup = sys.argv[:]
    sys.argv = ["check-prose.py", path]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = CHECK_CN.main()
    finally:
        sys.argv = argv_backup
        Path(path).unlink(missing_ok=True)
    return code, buf.getvalue()


# ---------------------------------------------------------- shared module

def test_mask_preserves_layout():
    text = "---\ntitle: t\n---\nab `x: y` cd\nef"
    masked = GR.mask_non_prose(text)
    check("mask 保持长度与换行", len(masked) == len(text)
          and masked.count("\n") == text.count("\n"))
    check("mask 抹掉行内代码中的冒号", GR.find_colons(masked) == [])


def test_mask_multiline_html_comment():
    text = "他走回家。\n<!-- 备注：\n稍后修改 -->\n他继续往前走。"
    masked = GR.mask_non_prose(text)
    check("mask 抹掉多行 HTML 注释", GR.find_colons(masked) == [])


def test_find_semicolons_both_widths():
    check("ASCII/全角分号都检出", GR.find_semicolons("a;b；c") == [1, 3])


def test_colon_dialogue_quote_fails():
    # Canonical rule is an unconditional prose colon ban
    # (templates/settings/global-rules.md `no-colon-in-prose`): the former
    # dialogue-attribution exemption was removed — attribution colons fail.
    check("CJK 引语冒号判失败", GR.find_colons("他说：“走吧。”") == [2])
    check("ASCII 引语冒号判失败", GR.find_colons('She said: "Run."') == [8])
    check("普通冒号仍检出", GR.find_colons("他说：时间到了。") == [2])


# ---------------------------------------------------------- EN hard rules

def test_en_colon_fails():
    fails = en_failures("She opened the box and found a note. It read: Run.")
    check("EN 正文冒号判失败", any("Colon" in f for f in fails))
    clean = en_failures("He arrived at noon and the room was empty.")
    check("EN 无冒号不误报", not any("Colon" in f for f in clean))


def test_en_semicolon_fails():
    fails = en_failures("He ran fast; she followed close behind.")
    check("EN 正文分号判失败", any("Semicolon" in f for f in fails))


def test_en_valid_dialogue_passes():
    fails = en_failures('"I told you," she said, "it is over." She turned away slowly.')
    check("EN 中断式单人对话不判失败", not any("dialogue" in f.lower() for f in fails))


def test_en_two_dialogues_fail():
    fails = en_failures('"I will go," Mara said. "Stay," Jin said. The door stayed open.')
    check("EN 一段两人对话判失败", any("dialogue" in f.lower() for f in fails))


def test_en_prose_only_scoping():
    base = "He walked home through the quiet evening street."
    cases = {
        "URL 中的冒号": f"He checked https://example.com:8080/docs and {base[3:]}",
        "frontmatter 中的冒号": f"---\ntitle: Test\nchapter: 3\n---\n{base}",
        "代码块中的冒号": f"```\nkey: value\n```\n{base}",
        "代码块中的分号": f"```\na = 1; b = 2;\n```\n{base}",
        "HTML 注释中的冒号": f"{base}\n<!-- note:\nfix later -->\nHe kept walking onward.",
        "行内代码中的冒号": f"The screen read `error: timeout` and {base[3:]}",
    }
    for name, text in cases.items():
        fails = en_failures(text)
        check(f"EN {name}不判失败",
              not any("Colon" in f or "Semicolon" in f for f in fails),
              fails[:1])


def test_en_em_dash_warning_only():
    text = "\n".join(
        f"He kept walking — block {i} — and never looked back at the empty street."
        for i in range(8)
    )
    result = CHECK_EN.check_text(text)
    check("EN 破折号过多出警告", any("dash" in w for w in result.warnings))
    check("EN 破折号永不判失败", not result.failures)


# ---------------------------------------------------------- CN hard rules

def test_cn_colon_fails_both_widths():
    code, out = run_cn("他说了一句话：时间到了。他转身走了。")
    check("CN 全角冒号判失败（退出码 1）", code == 1 and "冒号" in out, (code, out[:120]))
    code, out = run_cn("他说了一句话:时间到了。他转身走了。")
    check("CN 半角冒号判失败（退出码 1）", code == 1 and "冒号" in out, (code, out[:120]))


def test_cn_semicolon_fails_both_widths():
    code, out = run_cn("他跑得快；她紧跟在后面不放。")
    check("CN 全角分号判失败（退出码 1）", code == 1 and "分号" in out, (code, out[:120]))
    code, out = run_cn("他跑得快;她紧跟在后面不放。")
    check("CN 半角分号判失败（退出码 1）", code == 1 and "分号" in out, (code, out[:120]))


def test_cn_valid_dialogue_passes():
    code, out = run_cn("“我告诉过你，”她说，“结束了。”她转身走了。")
    check("CN 中断式单人对话不判失败（退出码 0）", code == 0, (code, out[:200]))
    code, _ = run_cn("“日期写错了。”\n老板看了一眼日期没有错。")
    check("CN 独立对话段不判失败（退出码 0）", code == 0, code)


def test_cn_two_dialogues_fail():
    code, out = run_cn("“我去。”马拉说。“留下。”金说。他转身走了。")
    check("CN 一段两人对话判失败", code == 1 and "对话" in out, (code, out[:200]))
    code, out = run_cn("“我去。”“你留下。”他转身走了。")
    check("CN 一段两引语无说话人信号判失败", code == 1 and "对话" in out, (code, out[:200]))


def test_cn_dialogue_colon_fails():
    code, out = run_cn("他顿了顿——没接话。他说：“走吧。”门关上了。")
    check("CN 引语冒号判失败（退出码 1）", code == 1 and "冒号" in out, (code, out[:200]))


def test_cn_prose_only_scoping():
    base = "他走在回家的路上心情格外平静。"
    cases = {
        "URL 中的冒号": "他打开网站 https://example.com:8080/docs 然后继续往前走了很久。",
        "frontmatter 中的冒号": f"---\ntitle: 测试章节\n---\n{base}",
        "代码块中的冒号": f"```\nkey: value\n```\n{base}",
        "代码块中的分号": f"```\na = 1; b = 2;\n```\n{base}",
        "多行 HTML 注释中的冒号": "他走在回家的路上心情平静。\n<!-- 备注：\n稍后修改 -->\n他继续往前走着没有停下。",
    }
    for name, text in cases.items():
        code, out = run_cn(text)
        check(f"CN {name}不判失败（退出码 0）", code == 0, (code, name, out[:160]))


def test_cn_em_dash_warning_only():
    code, out = run_cn("他顿了顿——先看左边——又看右边——最后盯着柜子不动了。")
    check("CN 破折号密集仅警告（退出码 0）",
          code == 0 and "破折号" in out and "需要人工判断" in out, (code, out[:200]))


# ---------------------------------------------------------- corpus tool

def run_corpus(tmpdir, argv_extra=()):
    argv_backup = sys.argv[:]
    sys.argv = ["check-emdash-corpus.py", str(tmpdir), *argv_extra]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = CORPUS.main()
    finally:
        sys.argv = argv_backup
    return code, buf.getvalue()


def test_corpus_counts_and_warns():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "ch01.md").write_text("He walked — on — and on through the night.\n", encoding="utf-8")
        (root / "ch02.md").write_text("He walked home through the quiet street.\n", encoding="utf-8")
        code, out = run_corpus(root)
        check("corpus 工具退出码恒为 0", code == 0, code)
        check("corpus 输出逐文件计数", "ch01.md: 2" in out and "ch02.md: 0" in out, out[:200])
        check("corpus 输出总量", "corpus total: 2" in out, out[:200])


def test_corpus_excess_warns_never_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "ch01.md").write_text("—a—b—c—d—e—f—\n", encoding="utf-8")
        code, out = run_corpus(root)
        check("corpus 超量警告但退出码仍为 0",
              code == 0 and "WARNING" in out, (code, out[:200]))


if __name__ == "__main__":
    test_mask_preserves_layout()
    test_mask_multiline_html_comment()
    test_find_semicolons_both_widths()
    test_colon_dialogue_quote_fails()
    test_en_colon_fails()
    test_en_semicolon_fails()
    test_en_valid_dialogue_passes()
    test_en_two_dialogues_fail()
    test_en_prose_only_scoping()
    test_en_em_dash_warning_only()
    test_cn_colon_fails_both_widths()
    test_cn_semicolon_fails_both_widths()
    test_cn_valid_dialogue_passes()
    test_cn_two_dialogues_fail()
    test_cn_dialogue_colon_fails()
    test_cn_prose_only_scoping()
    test_cn_em_dash_warning_only()
    test_corpus_counts_and_warns()
    test_corpus_excess_warns_never_fails()
    print(f"\n{summary()}")
    sys.exit(exit_code())
