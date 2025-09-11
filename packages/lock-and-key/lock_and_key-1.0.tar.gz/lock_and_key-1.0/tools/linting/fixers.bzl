load("@pip//:requirements.bzl", "requirement")

def _make_lint_fix(name, entry_point, deps):
    if entry_point == "black":
        cmd_command = "$(location //tools/linting:runner) {} $(locations //lock_and_key:all_py_files) && touch $@".format(entry_point)
    elif entry_point == "isort":
        cmd_command = "$(location //tools/linting:runner) {} $(locations //lock_and_key:all_py_files) && touch $@".format(entry_point)
    else:
        fail("Unsupported fixer: {}".format(entry_point))
    
    native.genrule(
        name = name + "_fix",
        srcs = ["//lock_and_key:all_py_files"],
        outs = [name + "_fix.stamp"],
        cmd = cmd_command,
        tools = ["//tools/linting:runner"],
    )

def black_fix(name = "black", deps = None):
    _make_lint_fix(name, "black", deps or [requirement("black")])

def isort_fix(name = "isort", deps = None):
    _make_lint_fix(name, "isort", deps or [requirement("isort")])