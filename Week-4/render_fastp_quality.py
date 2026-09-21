import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
json_path = ROOT / "results" / "fastp_DRR303595.json"
output_path = ROOT / "results" / "qc" / "figures" / "lamin_fastp_quality_before_after.svg"

with json_path.open(encoding="utf-8") as handle:
    data = json.load(handle)

width = 1600
height = 760
panel_width = 650
panel_height = 500
left_positions = (110, 840)
top = 165
y_min = 30
y_max = 40
colors = {"A": "#b09b32", "T": "#b44b9b", "C": "#2ca25f", "G": "#4666d8", "mean": "#333333"}


def point_path(values, left):
    points = []
    for index, value in enumerate(values):
        x = left + index / (len(values) - 1) * panel_width
        y = top + panel_height - ((value - y_min) / (y_max - y_min)) * panel_height
        points.append(f"{x:.2f},{y:.2f}")
    return "M " + " L ".join(points)


def panel(label, source, left):
    elements = [
        f'<text x="{left}" y="140" font-family="Arial, sans-serif" font-size="20" font-weight="bold">{label}</text>',
        f'<rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}" fill="white" stroke="#cccccc" />',
    ]
    for quality in range(y_min, y_max + 1, 2):
        y = top + panel_height - ((quality - y_min) / (y_max - y_min)) * panel_height
        elements.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + panel_width}" y2="{y:.2f}" stroke="#e6e6e6" />')
        elements.append(f'<text x="{left - 16}" y="{y + 5:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="14">{quality}</text>')
    for position in range(0, 151, 25):
        x = left + position / 150 * panel_width
        elements.append(f'<text x="{x:.2f}" y="{top + panel_height + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">{position}</text>')
    for quality in ("A", "T", "C", "G", "mean"):
        elements.append(f'<path d="{point_path(source["quality_curves"][quality], left)}" fill="none" stroke="{colors[quality]}" stroke-width="2" />')
    return "\n".join(elements)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white" />
<text x="{width / 2:.0f}" y="48" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="bold">Lamin read quality before and after filtering</text>
<text x="{width / 2:.0f}" y="92" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="#555">Quality score by base position</text>
<line x1="420" y1="112" x2="450" y2="112" stroke="#b09b32" stroke-width="3" /><text x="460" y="117" font-family="Arial, sans-serif" font-size="15">A</text>
<line x1="560" y1="112" x2="590" y2="112" stroke="#b44b9b" stroke-width="3" /><text x="600" y="117" font-family="Arial, sans-serif" font-size="15">T</text>
<line x1="700" y1="112" x2="730" y2="112" stroke="#2ca25f" stroke-width="3" /><text x="740" y="117" font-family="Arial, sans-serif" font-size="15">C</text>
<line x1="840" y1="112" x2="870" y2="112" stroke="#4666d8" stroke-width="3" /><text x="880" y="117" font-family="Arial, sans-serif" font-size="15">G</text>
<line x1="980" y1="112" x2="1010" y2="112" stroke="#333333" stroke-width="3" /><text x="1020" y="117" font-family="Arial, sans-serif" font-size="15">Mean</text>
{panel("Before filtering: read 1 quality", data["read1_before_filtering"], left_positions[0])}
{panel("After filtering: read 1 quality", data["read1_after_filtering"], left_positions[1])}
<text x="{width / 2:.0f}" y="{top + panel_height + 65}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16">Position in read (bp)</text>
<text x="35" y="{top + panel_height / 2:.0f}" text-anchor="middle" transform="rotate(-90 35 {top + panel_height / 2:.0f})" font-family="Arial, sans-serif" font-size="16">Quality score</text>
</svg>
'''

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg, encoding="utf-8")
print(output_path)
