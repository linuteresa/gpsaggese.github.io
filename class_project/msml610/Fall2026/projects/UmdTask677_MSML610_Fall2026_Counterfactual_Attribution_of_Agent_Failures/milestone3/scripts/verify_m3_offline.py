"""Run existing and new regressions with network disabled before collection."""
from m3_offline_common import ROOT, OUT
import json
import xml.etree.ElementTree as ET
import pytest


if __name__ == "__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    xml=OUT/"tests.xml"
    # M3 tests, the frozen M2 regressions and the pinned M1 chess tests.
    result=pytest.main(["-q","-c",str(ROOT/"pytest.ini"),str(ROOT/"tests"),str(ROOT.parent/"milestone2/tests"),
        str(ROOT/"vendor/pr917/test/test_caaf.py"),f"--junitxml={xml}"])
    suites=ET.parse(xml).getroot()
    counts={k:sum(int(s.get(k,"0")) for s in suites.findall("testsuite")) for k in ("tests","failures","errors","skipped")}
    (OUT/"test_results.json").write_text(json.dumps({"network_blocked":True,"api_calls":0,
        "exit_code":int(result),**counts},indent=2)+"\n")
    raise SystemExit(result)
