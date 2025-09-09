from __future__ import annotations

import argparse
import json
import sys

from nova.tools.doctor import NovaDoctor


def main(argv=None):
    p = argparse.ArgumentParser(description="Nova (AlwaysGreen) doctor")
    p.add_argument("--config", default=".github/nova.yml", help="Path to nova.yml")
    p.add_argument("--ci-cmd", default=None, help='Optional: run `nova fix --ci "<cmd>"` (mutating).')
    p.add_argument("--smoke", action="store_true", help="Enable smoke run (disabled by default).")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors for exit status.")
    args = p.parse_args(argv)

    doctor = NovaDoctor(
        config_path=args.config,
        ci_command=args.ci_cmd,
        enable_smoke_run=args.smoke,
        strict_warnings=args.strict,
    )
    result = doctor.run()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Minimal pretty print without extra deps
        ok = result.get("ok", False)
        print(f"Doctor: {'OK' if ok else 'ISSUES FOUND'}\n")
        for c in result.get("checks", []):
            mark = "✔" if c.get("ok") else ("!" if c.get("status") == "warn" else "✗")
            name = c.get("name", "check")
            status = c.get("status", "")
            detail = c.get("detail", "")
            print(f"{mark} {name}: {status}")
            if detail:
                print(f"   {detail}")

    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()


