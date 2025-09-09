from pathlib import Path
import textwrap
from nova.tools.safety_limits import SafetyConfig


def test_load_limits_from_yaml(tmp_path: Path):
    cfg = tmp_path / "nova.yml"
    cfg.write_text(textwrap.dedent(
        """
        limits:
          max_files_changed: 3
          max_loc_delta: 25
        blocked_paths:
          - ".github/workflows/"
          - "deploy/"
        """
    ).strip())

    sc = SafetyConfig(cfg)
    s = sc.safety_limits
    assert s.max_files_modified == 3
    assert s.max_lines_changed == 25
    assert any(p.endswith("workflows/") for p in s.restricted_paths)


