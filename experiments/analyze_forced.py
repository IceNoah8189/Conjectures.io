#!/usr/bin/env python3
"""Summarize exact membership tables and make an offline lattice viewer."""

import argparse
from collections import Counter
import json
from pathlib import Path


def analyze(report):
    rules = {name: [] for name in (
        "none_iff_other_two_corner_points_forced",
        "isolated_points_forced", "degree_one_points_never_none",
        "requiring_any_point_loses_at_most_one",
        "new_point_never_none", "new_point_forced_iff_jump",
        "requested_previous_prefix_jump_criterion",
        "no_none_implies_active_forced_points_in_one_residue",
        "none_in_one_residue_except_optional_bottom_boundary_pair",
    )}
    histograms = {name: Counter() for name in
                  ("status", "requirement_loss", "none_colour_count")}
    degree_status = Counter()
    colour_failures, multicolour, unique, all_flexible = [], [], [], []
    total_incident_pair_tests = 0
    for prefix in report["rows"]:
        t, g = prefix["t"], prefix["g"]
        points = prefix["points"]
        domain = {point["weight"] for point in points}
        forced = set(prefix["forced"])
        triples = [{n, 2*n, 3*n} for n in domain if 3*n in domain]
        incident = {n: [] for n in domain}
        for triple in triples:
            for n in triple:
                incident[n].append(triple)
        active = {n for n in domain if incident[n]}
        colours = [
            {point["weight"] for point in points
             if point["weight"] in active and (point["a"] - point["b"]) % 3 == r}
            for r in range(3)
        ]
        if min(map(len, colours)) != len(points) - g:
            colour_failures.append({
                "t": t, "minimum_omissions": len(points) - g,
                "active_colour_sizes": [len(colour) for colour in colours],
                "excess": min(map(len, colours)) - (len(points) - g),
            })
        none = [point for point in points if point["status"] == "none"]
        none_colours = Counter((point["a"] - point["b"]) % 3 for point in none)
        histograms["none_colour_count"][len(none_colours)] += 1
        if not none:
            forced_colours = {
                (point["a"] - point["b"]) % 3 for point in points
                if point["weight"] in forced & active
            }
            if len(forced_colours) > 1:
                rules["no_none_implies_active_forced_points_in_one_residue"].append(t)
        if len(none_colours) > 1:
            majority = none_colours.most_common(1)[0][0]
            off_colour = [point for point in none
                          if (point["a"] - point["b"]) % 3 != majority]
            coordinates = {(point["a"], point["b"]) for point in off_colour}
            is_bottom_pair = (len(coordinates) == 2 and any(
                b == 1 and (a + 2, 0) in coordinates for a, b in coordinates
            ))
            if not is_bottom_pair:
                rules["none_in_one_residue_except_optional_bottom_boundary_pair"].append(t)
            multicolour.append({
                "t": t, "majority_residue": majority,
                "counts": dict(none_colours),
                "off_colour_points": [
                    {key: point[key] for key in ("weight", "a", "b")}
                    for point in off_colour
                ],
            })
        if not prefix["flexible_count"]:
            unique.append(t)
        if not prefix["forced"] and not prefix["none"]:
            all_flexible.append(t)
        for point in points:
            n, status = point["weight"], point["status"]
            example = {"t": t, "weight": n, "a": point["a"], "b": point["b"]}
            degree = len(incident[n])
            pair_forced = any(triple - {n} <= forced for triple in incident[n])
            total_incident_pair_tests += 1
            if pair_forced != (status == "none"):
                rules["none_iff_other_two_corner_points_forced"].append(example)
            if degree == 0 and status != "forced":
                rules["isolated_points_forced"].append(example)
            if degree == 1 and status == "none":
                rules["degree_one_points_never_none"].append(example)
            loss = g - point["g_required"]
            if loss > 1:
                rules["requiring_any_point_loses_at_most_one"].append({**example, "loss": loss})
            histograms["status"][status] += 1
            histograms["requirement_loss"][loss] += 1
            degree_status[status, degree] += 1
        if points[-1]["status"] == "none":
            rules["new_point_never_none"].append(t)
        if not prefix["new_point_forced_iff_jump"]:
            rules["new_point_forced_iff_jump"].append(t)
        if not prefix["jump_test"]["matches"]:
            rules["requested_previous_prefix_jump_criterion"].append(t)
    return {
        "prefix_count": report["prefix_count"], "last_t": report["last_t"],
        "point_classifications": report["point_classifications"],
        "constrained_queries": report["constrained_queries"],
        "rules_tested": {name: {"fits_all_computed_cases": not failures,
                               "counterexamples": failures}
                         for name, failures in rules.items()},
        "incident_pair_rule_cases": total_incident_pair_tests,
        "histograms": {name: dict(counts) for name, counts in histograms.items()},
        "degree_status_counts": [
            {"status": status, "incident_corners": degree, "count": count}
            for (status, degree), count in sorted(degree_status.items())
        ],
        "unique_optimum_thresholds": unique,
        "all_points_flexible_thresholds": all_flexible,
        "simple_active_colour_cover_counterexamples": colour_failures,
        "none_in_multiple_residue_classes": multicolour,
        "interpretation": "Finite exact computations; fitted converses are not Lean proofs or established general formulae.",
    }


VIEWER = r"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maximum corner-free sets: forced points</title>
<style>
body{font:16px system-ui,sans-serif;margin:28px auto;padding:0 20px;max-width:1000px;color:#18232f;background:#fafbfc}
h1{font-size:25px}label,button,select{margin-right:12px}input[type=range]{width:min(550px,75vw)}
button,select{padding:5px 9px}#plot{max-width:100%;height:auto;background:white;border:1px solid #d6dbe0}
.legend{display:flex;gap:20px;flex-wrap:wrap;margin:15px 0}.dot{display:inline-block;width:13px;height:13px;border-radius:3px;margin-right:6px}
#summary{line-height:1.6}.note{font-size:14px;color:#45505d}a{color:#126576}
</style>
<h1>Points in every or no maximum corner-free set</h1>
<p>Move through the prefixes of the 3-smooth numbers. Hover over a point for
its coordinates and both constrained maxima.</p>
<p><button id="back">Previous</button><input id="slider" type="range" min="1">
<button id="forward">Next</button></p>
<p><label>Example <select id="examples"></select></label>
<label><input id="before" type="checkbox"> Show the prefix before the new number</label></p>
<div class="legend"><span><i class="dot" style="background:#087f8c"></i>Forced: in every optimum</span>
<span><i class="dot" style="background:#d14d24"></i>None: in no optimum</span>
<span><i class="dot" style="background:#bac3cc"></i>Flexible</span></div>
<p id="summary"></p><svg id="plot" xmlns="http://www.w3.org/2000/svg" role="img"></svg>
<p class="note">A black outline marks the new point. Purple outlines mark its
two lower neighbors when the previous prefix is shown. The diagonal residue
is (a−b) modulo 3. All classifications come from exact constrained optimization;
they are computational results, not Lean proofs.</p>
<p><a href="@@CSV@@">Full CSV table</a> · <a href="@@JSON@@">Exact-query report</a> ·
<a href="@@ANALYSIS@@">Pattern checks</a></p>
<script>
const data=@@DATA@@;
const slider=document.getElementById('slider'), before=document.getElementById('before');
const examples=document.getElementById('examples'), plot=document.getElementById('plot');
slider.max=data.rows.length; slider.value=data.rows.length;
for(const target of [6,18,162,324,1536,6144,12288,data.rows.at(-1).t]){
 const i=data.rows.findIndex(row=>row.t===target); if(i<0)continue;
 const option=document.createElement('option');option.value=i+1;option.textContent=`t = ${target}`;examples.append(option);
}
function node(name,attributes,text){const n=document.createElementNS('http://www.w3.org/2000/svg',name);
 for(const [k,v]of Object.entries(attributes))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;}
function draw(){
 const index=Number(slider.value)-1, current=data.rows[index], showPrevious=before.checked&&index>0;
 const row=showPrevious?data.rows[index-1]:current, points=data.points.slice(0,row.k);
 const fresh=data.points[index], lowers=new Set(fresh[2]>0?[fresh[0]/3,2*fresh[0]/3]:[]);
 const maxA=Math.max(...points.map(p=>p[1])),maxB=Math.max(...points.map(p=>p[2]));
 const spacing=29,width=80+(maxA+1)*spacing,height=90+(maxB+1)*spacing;
 plot.replaceChildren();plot.setAttribute('viewBox',`0 0 ${width} ${height}`);
 plot.setAttribute('width',width);plot.setAttribute('height',height);
 plot.append(node('text',{x:20,y:24,'font-size':15},`t = ${row.t}, g = ${row.g}`));
 for(let a=0;a<=maxA;a++)plot.append(node('text',{x:58+a*spacing,y:height-32,'font-size':11,'text-anchor':'middle'},a));
 for(let b=0;b<=maxB;b++)plot.append(node('text',{x:29,y:60+(maxB-b)*spacing+4,'font-size':11},b));
 plot.append(node('text',{x:width-30,y:height-31,'font-size':14},'a'));
 plot.append(node('text',{x:28,y:42,'font-size':14},'b'));
 const colors={F:'#087f8c',N:'#d14d24','.':'#bac3cc'}, names={F:'forced',N:'none','.':'flexible'};
 points.forEach(([weight,a,b],i)=>{
  const status=row.status[i],highlight=showPrevious&&lowers.has(weight),isNew=!showPrevious&&i===index;
  const box=node('rect',{x:47+a*spacing,y:49+(maxB-b)*spacing,width:22,height:22,rx:3,
   fill:colors[status],stroke:highlight?'#7f35b2':isNew?'#18232f':'none','stroke-width':highlight||isNew?3:0});
  box.append(node('title',{},`(${a}, ${b}), n = ${weight}, residue = ${((a-b)%3+3)%3}\n${names[status]}\nExcluded maximum: ${row.g-row.ex[i]}\nRequired maximum: ${row.g-row.req[i]}`));
  plot.append(box);
 });
 const counts=Object.fromEntries(['F','N','.'].map(c=>[c,[...row.status].filter(s=>s===c).length]));
 let criterion=fresh[2]===0?'The new number is a power of two.':
  `Previous statuses at ${fresh[0]/3} and ${2*fresh[0]/3}: ${current.lower.join(', ')}.`;
 document.getElementById('summary').textContent=`Prefix ${row.k}/${data.rows.length}; `+
  `${counts.F} forced, ${counts.N} none, ${counts['.']} flexible. `+
  `New threshold ${current.t}: ${current.jump?'jump':'no jump'}. ${criterion}`;
 examples.value=index+1;
}
slider.addEventListener('input',draw);before.addEventListener('change',draw);
document.getElementById('back').onclick=()=>{slider.value=Math.max(1,Number(slider.value)-1);draw();};
document.getElementById('forward').onclick=()=>{slider.value=Math.min(data.rows.length,Number(slider.value)+1);draw();};
examples.onchange=()=>{slider.value=examples.value;draw();};draw();
</script></html>
"""


def write_viewer(path, report, analysis_path, report_path):
    points = report["rows"][-1]["points"]
    data = {
        "points": [[point["weight"], point["a"], point["b"]] for point in points],
        "rows": [{
            "k": row["prefix"], "t": row["t"], "g": row["g"], "jump": row["jump"],
            "status": "".join({"forced": "F", "none": "N", "flexible": "."}[p["status"]]
                              for p in row["points"]),
            "ex": [row["g"] - p["g_excluded"] for p in row["points"]],
            "req": [row["g"] - p["g_required"] for p in row["points"]],
            "lower": row["jump_test"].get("previous_statuses", []),
        } for row in report["rows"]],
    }
    html = (VIEWER.replace("@@DATA@@", json.dumps(data, separators=(",", ":")))
            .replace("@@CSV@@", report_path.with_suffix(".csv").name)
            .replace("@@JSON@@", report_path.name)
            .replace("@@ANALYSIS@@", analysis_path.name))
    path.write_text(html)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, default=Path("experiments/forced-analysis.json"))
    parser.add_argument("--viewer", type=Path, default=Path("experiments/forced-viewer.html"))
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    summary = analyze(report)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    write_viewer(args.viewer, report, args.output, args.report)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
