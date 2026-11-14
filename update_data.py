"""매일 갱신: 드라이브의 vera_regime_bundle.json.gz(또는 풀린 json)를 받아 data.js의 해당 키만 바꾼다.
사용: python update_data.py <bundle 경로>
바뀐 게 없으면 '변경 없음'을 출력하고 종료 코드 0, 바뀌면 '갱신 <asof>'를 출력.
번들 수집 시각(info의 collected)이 data.js 것과 같거나 더 이르면 덮어쓰지 않는다(예전 번들로 되돌아가는 것 방지).
번들에 새 규칙 파일(trig2 등)이 없으면 data.js에 남은 예전 날짜의 새 규칙 파일을 지운다(화면은 이전 규칙 비중과 안내문으로 바뀜)."""
import gzip, json, pathlib, sys

H = pathlib.Path(__file__).resolve().parent
NEW_RULE = ("trig2", "anlg2", "sim2", "ep2", "curve2", "recent2", "chg2", "tele2")


def collected(rows):
    for r in rows or []:
        if isinstance(r, dict) and r.get("key") == "collected":
            return str(r.get("value") or "")
    return ""


src = pathlib.Path(sys.argv[1])
raw = src.read_bytes()
b = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
js = (H / "data.js").read_text(encoding="utf-8")
pre = "window.__DATA__ = "
d = json.loads(js[len(pre):].rstrip().rstrip(";"))
files = b["files"]
new_c = collected(files.get("info")) or str((b.get("manifest") or {}).get("collected") or "")
old_c = collected(d.get("info"))
if new_c and old_c and new_c <= old_c:
    print(f"번들 수집 {new_c} / data.js {old_c}: 같은 회차이거나 더 이른 번들이라 건너뜀", file=sys.stderr)
    print("변경 없음")
    sys.exit(0)
for k, v in files.items():
    d[k] = v
if "trig2" not in files:
    for k in NEW_RULE:
        d.pop(k, None)
out = pre + json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
if out == js:
    print("변경 없음")
    sys.exit(0)
(H / "data.js").write_text(out, encoding="utf-8")
print("갱신", b["manifest"].get("asof"), b["manifest"].get("summary", ""))
