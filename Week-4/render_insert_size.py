import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
json_path = ROOT / "results" / "fastp_DRR303595.json"
output_path = ROOT / "results" / "qc" / "figures" / "lamin_insert_size_distribution.svg"

with json_path.open(encoding="utf-8") as handle:
    data = json.load(handle)

histogram = data["insert_size"]["histogram"]
peak = data["insert_size"]["peak"]
plot_width = 1000
plot_height = 520
left = 90
right = 35
top = 70
bottom = 75
chart_width = plot_width - left - right
chart_height = plot_height - top - bottom
max_value = max(histogram)
bar_width = chart_width / len(histogram)

bars = []
for index, value in enumerate(histogram):
    height = value / max_value * chart_height if max_value else 0
    x = left + index * bar_width
    y = top + chart_height - height
    bars.append(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(bar_width, 0.5):.2f}" '
        f'height="{height:.2f}" fill="#287db5" />'
    )

ticks = []
for value in range(0, len(histogram), 100):
    x = left + value * bar_width
    ticks.append(
        f'<line x1="{x:.2f}" y1="{top + chart_height}" x2="{x:.2f}" '
        f'y2="{top + chart_height + 8}" stroke="#333" />'
        f'<text x="{x:.2f}" y="{top + chart_height + 30}" text-anchor="middle" '
        f'font-size="14">{value}</text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{plot_width}" height="{plot_height}" viewBox="0 0 {plot_width} {plot_height}">
<rect width="100%" height="100%" fill="white" />
<text x="{plot_width / 2:.0f}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="22">Lamin insert size distribution</text>
<text x="{plot_width / 2:.0f}" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-size="14">Peak insert size: {peak} bp</text>
<line x1="{left}" y1="{top + chart_height}" x2="{left + chart_width}" y2="{top + chart_height}" stroke="#333" />
<line x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_height}" stroke="#333" />
{''.join(bars)}
{''.join(ticks)}
<text x="{left + chart_width / 2:.0f}" y="{plot_height - 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16">Insert size (bp)</text>
<text x="20" y="{top + chart_height / 2:.0f}" text-anchor="middle" transform="rotate(-90 20 {top + chart_height / 2:.0f})" font-family="Arial, sans-serif" font-size="16">Read count</text>
</svg>
'''

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg, encoding="utf-8")
print(output_path)