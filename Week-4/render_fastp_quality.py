import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
json_path = ROOT / "results" / "fastp_DRR303595.json"
output_path = ROOT / "results" / "qc" / "figures" / "lamin_fastp_quality_before_after.svg"

with json_path.open(encoding="utf-8") as handle:
    data = json.load(handle)

width = 1200
height = 620
panel_width = 500
panel_height = 420
left_positions = (90, 650)
top = 110
colors = {"A": "#b09b32", "T": "#b44b9b", "C": "#2ca25f", "G": "#4666d8", "mean": "#333333"}


def point_path(values, left):
    points = []
    for index, value in enumerate(values):
        x = left + index / (len(values) - 1) * panel_width
        y = top + panel_height - (value / 40) * panel_height
        points.append(f"{x:.2f},{y:.2f}")
    return "M " + " L ".join(points)


def panel(label, source, left):
    elements = [
        f'<text x="{left}" y="80" font-family="Arial, sans-serif" font-size="18" font-weight="bold">{label}</text>',
        f'<rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}" fill="white" stroke="#cccccc" />',
    ]
    for quality in (20, 25, 30, 35, 40):
        y = top + panel_height - (quality / 40) * panel_height
        elements.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + panel_width}" y2="{y:.2f}" stroke="#e6e6e6" />')
        elements.append(f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12">{quality}</text>')
    for position in range(0, 151, 25):
        x = left + position / 150 * panel_width
        elements.append(f'<text x="{x:.2f}" y="{top + panel_height + 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{position}</text>')
    for quality in ("A", "T", "C", "G", "mean"):
        elements.append(f'<path d="{point_path(source["quality_curves"][quality], left)}" fill="none" stroke="{colors[quality]}" stroke-width="2" />')
    return "\n".join(elements)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white" />
<text x="{width / 2:.0f}" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold">Lamin read quality before and after filtering</text>
{panel("Before filtering: read 1 quality", data["read1_before_filtering"], left_positions[0])}
{panel("After filtering: read 1 quality", data["read1_after_filtering"], left_positions[1])}
<text x="{width / 2:.0f}" y="{top + panel_height + 55}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Position in read (bp)</text>
<text x="30" y="{top + panel_height / 2:.0f}" text-anchor="middle" transform="rotate(-90 30 {top + panel_height / 2:.0f})" font-family="Arial, sans-serif" font-size="14">Quality score</text>
<text x="1080" y="{top + 20}" font-family="Arial, sans-serif" font-size="13">A</text><line x1="1050" y1="{top + 15}" x2="1075" y2="{top + 15}" stroke="#b09b32" stroke-width="2" />
<text x="1080" y="{top + 45}" font-family="Arial, sans-serif" font-size="13">T</text><line x1="1050" y1="{top + 40}" x2="1075" y2="{top + 40}" stroke="#b44b9b" stroke-width="2" />
<text x="1080" y="{top + 70}" font-family="Arial, sans-serif" font-size="13">C</text><line x1="1050" y1="{top + 65}" x2="1075" y2="{top + 65}" stroke="#2ca25f" stroke-width="2" />
<text x="1080" y="{top + 95}" font-family="Arial, sans-serif" font-size="13">G</text><line x1="1050" y1="{top + 90}" x2="1075" y2="{top + 90}" stroke="#4666d8" stroke-width="2" />
<text x="1080" y="{top + 120}" font-family="Arial, sans-serif" font-size="13">Mean</text><line x1="1050" y1="{top + 115}" x2="1075" y2="{top + 115}" stroke="#333333" stroke-width="2" />
</svg>
'''

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg, encoding="utf-8")
print(output_path)
