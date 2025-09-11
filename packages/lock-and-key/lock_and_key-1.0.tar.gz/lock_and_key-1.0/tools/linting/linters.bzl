load("@pip//:requirements.bzl", "requirement")

def _make_lint_check(name, entry_point, deps):
    if entry_point == "black":
        cmd_command = "$(location //tools/linting:runner) {} --check --diff --line-length 120 $(locations //lock_and_key:all_py_files) > $@ 2>&1 && echo '{}: No formatting issues' > $@ || (echo '{} formatting issues found:' && $(location //tools/linting:runner) {} --check --diff --line-length 120 $(locations //lock_and_key:all_py_files) 2>&1| tee $@ && exit 1)".format(entry_point, name.title(), name.title(), entry_point)
    elif entry_point == "isort":
        cmd_command = "$(location //tools/linting:runner) {} --check-only --diff --profile black --line-length 120 $(locations //lock_and_key:all_py_files) > $@ 2>&1 && echo '{}: No import issues' > $@ || (echo '{} import sorting issues found:' && $(location //tools/linting:runner) {} --check-only --diff --profile black --line-length 120 $(locations //lock_and_key:all_py_files) 2>&1 | tee $@ && exit 1)".format(entry_point, name.title(), name.title(), entry_point)
    elif entry_point == "flake8":
        cmd_command = "$(location //tools/linting:runner) {} --max-line-length=120 $(locations //lock_and_key:all_py_files) > $@ 2>&1 && echo '{}: No issues found' > $@ || (echo '{} issues found:' && $(location //tools/linting:runner) {} --max-line-length=120 $(locations //lock_and_key:all_py_files) 2>&1 | tee $@ && exit 1)".format(entry_point, name.title(), name.title(), entry_point)
    elif entry_point == "mypy":
        cmd_command = "$(location //tools/linting:runner) {} $(locations //lock_and_key:all_py_files) > $@ 2>&1 && echo '{}: No type issues found' > $@ || (echo '{} type issues found:' && $(location //tools/linting:runner) {} $(locations //lock_and_key:all_py_files) 2>&1 | tee $@ && exit 1)".format(entry_point, name.title(), name.title(), entry_point)
    else:
        fail("Unsupported linter: {}".format(entry_point))
    
    native.genrule(
        name = name + "_check",
        srcs = ["//lock_and_key:all_py_files"],
        outs = [name + "_report.txt"],
        cmd = cmd_command,
        tools = ["//tools/linting:runner"],
    )

def black_lint(name = "black", deps = None):
    _make_lint_check(name, "black", deps or [requirement("black")])

def isort_lint(name = "isort", deps = None):
    _make_lint_check(name, "isort", deps or [requirement("isort")])

def flake8_lint(name = "flake8", deps = None):
    _make_lint_check(name, "flake8", deps or [requirement("flake8")])

def mypy_lint(name = "mypy", deps = None):
    _make_lint_check(name, "mypy", deps or [
        requirement("mypy"),
        requirement("pydantic"),
        requirement("click"),
        requirement("rich"),
    ])
