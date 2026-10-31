"""매일 갱신: 드라이브의 vera_regime_bundle.json.gz(또는 풀린 json)를 받아 data.js의 해당 키만 바꾼다.
사용: python update_data.py <bundle 경로>
바뀐 게 없으면 '변경 없음'을 출력하고 종료 코드 0, 바뀌면 '갱신 <asof>'를 출력."""
import gzip, json, pathlib, sys
H = pathlib.Path(__file__).resolve().parent
src = pathlib.Path(sys.argv[1])
raw = src.read_bytes()
b = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
js = (H / "data.js").read_text(encoding="utf-8")
pre = "window.__DATA__ = "
d = json.loads(js[len(pre):].rstrip().rstrip(";"))
for k, v in b["files"].items(): d[k] = v
out = pre + json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
if out == js: print("변경 없음"); sys.exit(0)
(H / "data.js").write_text(out, encoding="utf-8")
print("갱신", b["manifest"].get("asof"), b["manifest"].get("summary", ""))
