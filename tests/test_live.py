"""Test cửa sổ chơi trực tiếp (chonoi.live). Chỉ dành cho starter Python: nhóm đổi ngôn ngữ thì xóa file này."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read()


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code


@unittest.skipUnless(shutil.which("node"), "HUD JavaScript checks require Node.js")
class LiveHudTest(unittest.TestCase):
    """Execute the shipped client with a tiny DOM; no sim freshness dependency."""

    def test_phase4_three_context_warnings_and_contrast_toggle(self):
        self.run_client(r"""
snap={phase:'gather',screen:'playing',state:'playing',player:{pos:[60,20],oxygen_ticks:100,oxygen_max_ticks:400},
  monsters:[{pos:[65,20]}],meta:{monsters:{detect_radius:10}}};
updateWarnings();
assert.equal(elements.get('warning-panel').hidden,false);
assert.equal(elements.get('warning-monster').hidden,false);
assert.equal(elements.get('warning-oxygen').hidden,false);
snap={phase:'quan',screen:'playing',state:'playing',meta:{patience_s:60},customers:[{patience_ticks_left:900}]};
updateWarnings();
assert.equal(elements.get('warning-customer').hidden,false);
assert.equal(elements.get('warning-monster').hidden,true);
snap={phase:'gather',screen:'playing',state:'paused',player:{pos:[60,20],oxygen_ticks:1,oxygen_max_ticks:400}};
updateWarnings();
assert.equal(elements.get('warning-panel').hidden,true);
""")

    def run_client(self, checks):
        html = (Path(__file__).resolve().parents[1] / "chonoi/web/index.html").read_text(encoding="utf-8")
        script = html.split("<script>", 1)[1].split("</script>", 1)[0]
        harness = r"""
const assert = require('node:assert/strict');
class Element {
  constructor(){this.children=[];this.hidden=true;this.style={};this.textContent='';this.className='';this.classList={toggle(){}};}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=children;this.textContent='';}
  setAttribute(key,value){this[key]=value;}
  getContext(){return {};}
}
const elements=new Map();
const document={getElementById(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},
  createElement(){return new Element();},querySelectorAll(){return [];},body:new Element()};
const performance={now:()=>0};
const addEventListener=()=>{}, requestAnimationFrame=()=>{}, setTimeout=()=>{};
const fetch=()=>new Promise(()=>{});
"""
        fd, js_path = tempfile.mkstemp(prefix="chonoi-live-", suffix=".js")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(harness + script + checks)
            result = subprocess.run(["node", js_path],
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        finally:
            if os.path.exists(js_path):
                os.unlink(js_path)

    def test_individual_freshness_threshold_and_reserved_ids(self):
        self.run_client(r"""
const items=[{id:'I1',kind:'ca_loc',fresh:30},{id:'I2',kind:'ca_loc',fresh:29.996},
  {id:'I3',kind:'bong_sung',fresh:97.5}];
const original=JSON.stringify(items), parent=new Element();
renderInventory(parent,items,[{reserved:['I1']}]);
assert.equal(parent.children.length,3);
assert.match(parent.children[0].children[0].textContent,/30.00%.*giữ chỗ/);
assert.doesNotMatch(parent.children[0].className,/spoiled/);
assert.match(parent.children[1].className,/spoiled/);
assert.match(parent.children[1].children[0].textContent,/ươn/);
assert.equal(parent.children[2].children[1].value,97.5);
assert.equal(JSON.stringify(items),original);
assert.deepEqual(availableStock({stock:items,customers:[{reserved:['I1']}]}),[items[2]]);
""")

    def test_legacy_and_missing_inventory_fields(self):
        self.run_client(r"""
assert.deepEqual(inventoryCounts(['ca_loc','ca_loc','bong_sung']),{ca_loc:2,bong_sung:1});
assert.deepEqual(inventoryCounts(),{});
const parent=new Element();renderInventory(parent,{ca_loc:2});
assert.match(parent.children[0].children[0].textContent,/cá lóc ×2/);
assert.equal(parent.children[0].children.length,1);
renderInventory(parent,undefined);assert.equal(parent.textContent,'(trống)');
assert.deepEqual(availableStock({stock:{ca_loc:3},customers:[{reserved:{ca_loc:2}},{}]}),{ca_loc:1});
snap={mode:'gather'};updateFlow();updateInventoryHud();
assert.equal(elements.get('flow').hidden,true);
assert.equal(elements.get('inventory-title').textContent,'Giỏ 0');
""")

    def test_spoiled_event_before_another_event_is_not_skipped_or_repeated(self):
        self.run_client(r"""
snap={events:[{tick:1,name:'spoiled',data:{item_id:'I2',kind:'ca_loc',location:'hold'}},
  {tick:1,name:'gather',data:{}}]};
updateNotifications();assert.equal(notifications.length,2);
assert.match(notifications[0].text,/I2.*ươn.*giỏ/);assert.equal(notifications[0].tone,'danger');
updateNotifications();assert.equal(notifications.length,2);
snap.events.push({tick:2,name:'spoiled',data:{item_id:'I3',kind:'bong_sung',location:'stock'}});
updateNotifications();assert.equal(notifications.length,3);assert.match(notifications[2].text,/I3.*kho/);
""")

    def test_basket_and_instructions_have_separate_elements(self):
        self.run_client(r"""
snap={phase:'gather',screen:'playing',hold:[{id:'I1',kind:'ca_loc',fresh:88}],hold_capacity:12};
updateInventoryHud();assert.equal(elements.get('inventory-title').textContent,'Giỏ 1/12');
assert.match(elements.get('key-help').textContent,/Space bắt cá/);
assert.match(elements.get('inventory-list').children[0].children[0].textContent,/88.00%/);
snap={phase:'quan',screen:'playing',stock:[{id:'I2',kind:'ca_loc',fresh:29}],customers:[]};
updateInventoryHud();assert.match(elements.get('inventory-title').textContent,/Kho 1.*trống/);
assert.match(elements.get('inventory-list').children[0].className,/spoiled/);
""")

    def test_shop_individual_stock_and_legacy_count_stock(self):
        self.run_client(r"""
snap={phase:'shop',screen:'playing',day:1,money:0,earned:0,score:300,time_left_ticks:600,
  shop:{upgrades:{}},stock:[{id:'I4',kind:'ca_linh',fresh:20}]};
updateFlow();
const lists=elements.get('flow-content').children.filter(el=>el.className==='inventory-list');
assert.equal(lists.length,1);assert.match(lists[0].children[0].children[0].textContent,/I4.*ươn/);
snap.stock={ca_loc:2};updateFlow();
const legacy=elements.get('flow-content').children.find(el=>el.className==='inventory-list');
assert.match(legacy.children[0].children[0].textContent,/cá lóc ×2/);
""")


class LiveServerTest(unittest.TestCase):
    def test_auto_transition_carries_gather_inventory_into_quan(self):
        tuning = load_contract()["tuning"]
        # P3 [THAY THẾ]: giỏ và kho là mảng cá thể {id,kind,fresh} (contract v1.2), không còn kho đếm.
        scenario = {"hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100},
                             {"id": "I2", "kind": "bong_sung", "fresh": 100}], "time_left_ticks": 1}
        game = LiveGame("gather", tuning, scenario, 1)

        game._tick_once()

        self.assertEqual(game.mode, "quan")
        stock = game.session.snapshot()["stock"]
        self.assertEqual([(it["id"], it["kind"]) for it in stock], [("I1", "ca_loc"), ("I2", "bong_sung")])
        # hao một bước gather (0.5/s), bàn giao cùng tick không hao thêm
        for it in stock:
            self.assertAlmostEqual(it["fresh"], 100 - 0.5 / 60, delta=0.01)
        self.assertEqual(game.session.tick, 0)
        state = json.loads(game.state_json())
        self.assertEqual(state["mode"], "quan")
        self.assertEqual(state["meta"], tuning["quan"])
        game._tick_once()
        self.assertEqual(game.session.tick, 1)
        game.restart()
        self.assertEqual(game.mode, "gather")

    def test_auto_transition_can_be_disabled(self):
        tuning = load_contract()["tuning"]
        scenario = {"time_left_ticks": 1}
        game = LiveGame("gather", tuning, scenario, 1, auto_transition=False)

        game._tick_once()

        self.assertEqual(game.mode, "gather")
        self.assertTrue(game.session.done)
        self.assertEqual(game.session.sim.reason, "time")

    def test_state_input_and_clean_stop(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertIn("live_metrics", st)
            self.assertIn("ticks", st["live_metrics"])
            code, metrics = _get(base + "/metrics")
            self.assertEqual(code, 200)
            self.assertIn("live_metrics", json.loads(metrics))
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())


if __name__ == "__main__":
    unittest.main()
