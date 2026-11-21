"""Phase 4: giao diện bench_cmd và công thức benchmark v1.3."""

import contextlib
import io
import json
import math
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import bench


ROOT = Path(__file__).resolve().parents[1]
KEYS = {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"}


class BenchP4Test(unittest.TestCase):
    def test_contract_command_duration(self):
        contract = json.loads((ROOT / "game.contract.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bench.json"
            command = shlex.split(contract["bench_cmd"]) + [
                "--seed", "42", "--duration", "1", "--out", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                    text=True, timeout=30)
            if (result.returncode != 0
                    and "PermissionError: [Errno 1] Operation not permitted" in result.stderr
                    and "socket.bind" in result.stderr):
                self.skipTest("Sandbox chặn mở socket live")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(set(data), KEYS)
        for key, value in data.items():
            self.assertIn(type(value), (int, float), key)
            self.assertTrue(math.isfinite(value), key)
        self.assertGreater(data["frames"], 0)
        self.assertGreater(data["measured_s"], 0)
        self.assertGreater(data["load_ms"], 0)
        self.assertAlmostEqual(data["avg_fps"], data["frames"] / data["measured_s"])
        self.assertLessEqual(data["p1_low_fps"], data["avg_fps"])

    def test_low_fps_uses_slowest_frame_times_and_rounds_count_up(self):
        # 101 frames => ceil(1.01) = 2; mean of 0.1s and 0.3s => 5 FPS.
        self.assertAlmostEqual(bench.percentile_low([0.01] * 99 + [0.1, 0.3]), 5.0)
        self.assertAlmostEqual(bench.percentile_low([0.25]), 4.0)

    def test_measurement_excludes_warmup_and_load_uses_first_response(self):
        clock = [10.0]

        def read_frame():
            clock[0] += 0.25
            return b"{}"

        with patch.object(bench, "LiveGame"), patch.object(bench, "LiveServer") as server:
            server.return_value.url = "http://127.0.0.1/"
            with patch.object(bench.time, "perf_counter", side_effect=lambda: clock[0]):
                with patch.object(bench.urllib.request, "urlopen") as request:
                    request.return_value.__enter__.return_value.read.side_effect = read_frame
                    result = bench.run_bench(warmup_s=0.5, measure_s=0.5, launch_started=9.5)
            server.return_value.stop.assert_called_once_with()
        self.assertEqual(result, {"avg_fps": 4.0, "p1_low_fps": 4.0,
                                  "frames": 2, "measured_s": 0.5, "load_ms": 750.0})

    def test_cli_defaults_and_legacy_alias(self):
        for flags, duration in (([], 30.0), (["--measure-s", "1"], 1.0)):
            with self.subTest(flags=flags), patch.object(bench, "run_bench", return_value={}) as run:
                with patch.object(bench, "write_json"), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(bench.main(flags), 0)
                run.assert_called_once_with(42, 3.0, duration, 1280, 720,
                                            launch_started=bench.LAUNCH_STARTED)


if __name__ == "__main__":
    unittest.main()
