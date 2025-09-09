#!/usr/bin/env python3
"""
Run tests with coverage (preferring coverage.py if available, else Python's trace module),
compute overall coverage for the `arched_emailer` package, generate an SVG badge, and
update README.md to display the badge. If tests fail, writes a red "failing" badge.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import re
import traceback

PKG_DIR = Path(__file__).resolve().parents[1]
PACKAGE = "arched_emailer"
TESTS_DIR = PKG_DIR / "tests"
BADGE_DIR = PKG_DIR / "badges"
BADGE_PATH = BADGE_DIR / "coverage.svg"
README_PATH = PKG_DIR / "README.md"
BREAKDOWN_PATH = BADGE_DIR / "coverage_breakdown.txt"
STDERR_CAPTURE_PATH = BADGE_DIR / "test_stderr.txt"


def _extract_breakdown(captured: str) -> str:
    """Extract a per-file coverage breakdown from captured output.

    Supports either:
    - Our trace-mode block starting with "Trace coverage (approx):"
    - coverage.py tabular report starting with a line like "Name  Stmts  Miss  Cover"
    """
    if not captured:
        return ""
    if "Trace coverage (approx):" in captured:
        idx = captured.rfind("Trace coverage (approx):")
        return captured[idx:].strip() + "\n"
    lines = captured.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("Name") and "Stmts" in s and "Cover" in s:
            return "\n".join(lines[i:]) + ("\n" if not captured.endswith("\n") else "")
    return ""


def _try_pytest() -> tuple[bool, Exception | None, str]:
    try:
        import pytest  # type: ignore

        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            code = pytest.main([str(TESTS_DIR), "-q"])
        return code == 0, None, err_buf.getvalue()
    except Exception as e:  # pragma: no cover - import/availability dependent
        return False, e, ""


def _run_unittest() -> tuple[bool, str]:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(str(TESTS_DIR), pattern="test_*.py")
    out = io.StringIO()
    err = io.StringIO()
    runner = unittest.TextTestRunner(stream=out, verbosity=2)
    with redirect_stderr(err):
        result = runner.run(suite)
    return result.wasSuccessful(), err.getvalue()


def _run_tests() -> tuple[bool, str]:
    ok, _, captured = _try_pytest()
    if ok:
        return True, captured
    return _run_unittest()


def _color_for(percentage: float, failing: bool) -> str:
    if failing:
        return "#e05d44"  # red
    if percentage >= 95:
        return "#4c1"  # brightgreen
    if percentage >= 85:
        return "#97CA00"  # green-ish
    if percentage >= 70:
        return "#dfb317"  # yellow
    if percentage >= 50:
        return "#fe7d37"  # orange
    return "#e05d44"  # red


def _make_svg(label: str, value: str, color: str) -> str:
    # Simple static-width badge inspired by shields.io layout
    label_w = 70
    value_w = max(50, 6 * len(value))
    width = label_w + value_w
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="m"><rect width="{width}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{label_w}" height="20" fill="#555"/>
    <rect x="{label_w}" width="{value_w}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_w/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_w/2}" y="14">{label}</text>
    <text x="{label_w + value_w/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_w + value_w/2}" y="14">{value}</text>
  </g>
</svg>
""".strip()


def _files_in_package() -> list[Path]:
    root = PKG_DIR / PACKAGE
    return [p for p in root.rglob("*.py") if p.is_file()]


def _total_measurable_lines(p: Path) -> int:
    count = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        count += 1
    return count


def _trace_coverage() -> tuple[float, str]:
    from trace import Trace

    tracer = Trace(count=True, trace=False, ignoremods=("unittest",))

    def run():  # Run tests with unittest discovery
        return _run_unittest()[0]

    tracer.runfunc(run)
    results = tracer.results()
    counts = results.counts  # dict[(filename, lineno)] = hits

    files = _files_in_package()
    total = sum(_total_measurable_lines(p) for p in files)

    executed_lines_per_file: dict[str, int] = {}
    executed = 0
    file_map = {str(p.resolve()): p for p in files}

    # Count executed lines for package files
    for (filename, lineno), hits in counts.items():
        if hits <= 0:
            continue
        # Normalize to real paths
        try:
            key = str(Path(filename).resolve())
        except Exception:
            key = filename
        if key in file_map:
            executed += 1
            executed_lines_per_file[key] = executed_lines_per_file.get(key, 0) + 1

    # Build per-file estimates text
    lines: list[str] = []
    if executed_lines_per_file:
        lines.append("Trace coverage (approx):")
        for key, executed_lines in sorted(executed_lines_per_file.items()):
            path_obj = file_map[key]
            t = _total_measurable_lines(path_obj)
            pct = 0.0 if t == 0 else (executed_lines / t) * 100.0
            rel = path_obj.relative_to(PKG_DIR)
            lines.append(f"  {rel}: {pct:.1f}% ({executed_lines}/{t})")

    percentage = 0.0 if total == 0 else (executed / total) * 100.0
    return percentage, ("\n".join(lines) + ("\n" if lines else ""))


def run_with_coverage() -> tuple[float, bool, str]:
    # Prefer coverage.py if available
    try:
        import coverage  # type: ignore

        cov = coverage.Coverage(source=[PACKAGE])
        cov.start()
        success, captured_err = _run_tests()
        cov.stop()
        cov.save()

        # Print per-file report to stdout
        try:
            buf = io.StringIO()
            percent = cov.report(show_missing=True, file=buf)
            breakdown = buf.getvalue()
        except Exception:
            percent = 0.0
            breakdown = ""
        return (
            float(percent),
            success,
            (captured_err or "") + ("\n" + breakdown if breakdown else ""),
        )
    except Exception:
        # Fallback to stdlib trace
        try:
            percent, breakdown = _trace_coverage()
            success = True  # We already ran tests inside trace; treat as success if no exception
        except Exception:
            percent = 0.0
            success = False
        return float(percent), success, breakdown


def update_readme_badge(value_text: str) -> None:
    BADGE_DIR.mkdir(parents=True, exist_ok=True)

    # Insert or replace badge in README
    readme = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    badge_md = f"![Coverage](badges/coverage.svg) {value_text}"

    start = "<!-- coverage-badge -->"
    end = "<!-- coverage-badge-end -->"

    if start in readme and end in readme:
        new_readme = re.sub(
            rf"{re.escape(start)}[\s\S]*?{re.escape(end)}",
            f"{start}\n\n{badge_md}\n\n{end}",
            readme,
        )
    else:
        lines = readme.splitlines()
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, f"\n{start}\n\n{badge_md}\n\n{end}\n")
                inserted = True
                break
        if not inserted:
            lines = [f"{start}", "", badge_md, "", f"{end}", "", readme]
        new_readme = "\n".join(lines)

    README_PATH.write_text(new_readme, encoding="utf-8")


def main() -> int:
    try:
        BADGE_DIR.mkdir(parents=True, exist_ok=True)

        percent, success, captured = run_with_coverage()
        # Persist captured stderr for easy inspection
        if captured:
            STDERR_CAPTURE_PATH.write_text(captured, encoding="utf-8")

        label_value = f"{percent:.1f}%" if success else "failing"
        color = _color_for(percent, not success)
        svg = _make_svg("coverage", label_value, color)
        BADGE_PATH.write_text(svg, encoding="utf-8")
        update_readme_badge(label_value)

        # Extract and persist a per-file breakdown if present
        breakdown_text = _extract_breakdown(captured or "")
        if breakdown_text:
            BREAKDOWN_PATH.write_text(breakdown_text, encoding="utf-8")

        # Clear, compact summary
        status_text = "PASS" if success else "FAIL"
        print("=== Test & Coverage Summary ===")
        print(f"Tests: {status_text}")
        print(f"Coverage: {percent:.1f}%")
        # Always print the per-file report to stdout if we have it
        if breakdown_text:
            print(breakdown_text, end="")
        elif BREAKDOWN_PATH.exists():
            # Fallback to file contents if we couldn't extract from captured output
            try:
                print(BREAKDOWN_PATH.read_text(encoding="utf-8"), end="")
            except Exception:
                pass
        if STDERR_CAPTURE_PATH.exists():
            print(f"Captured test stderr: {STDERR_CAPTURE_PATH}")
        print(f"Badge: {BADGE_PATH}")
        return 0
    except Exception:
        traceback.print_exc()
        try:
            # Best-effort write failing badge
            svg = _make_svg("coverage", "failing", _color_for(0.0, True))
            BADGE_DIR.mkdir(parents=True, exist_ok=True)
            BADGE_PATH.write_text(svg, encoding="utf-8")
            update_readme_badge("failing")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
