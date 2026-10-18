"""Add reproducible scientific callouts around real IGV screenshot evidence.

Original screenshot pixels remain unchanged; overlays are separate output figures.
Coordinates are calibrated to the saved IGV layout, not new synthetic read data.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

root = Path(__file__).resolve().parents[1]
selected = json.loads((root/'results/igv_selected_variants.json').read_text())
manifest = []
for i, candidate in enumerate(selected, 1):
    source = root/f'png/06_candidate_{i}.png'
    pixels = plt.imread(source)
    height, width = pixels.shape[:2]
    # All saved candidate closeups have the same 82-base ruler and track layout.
    x = 0.575 * width
    fig = plt.figure(figsize=(width/100+4.8, height/100), dpi=100)
    ax = fig.add_axes([0, 0, width/(width+480), 1])
    ax.imshow(pixels)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis('off')
    boxes = [(x-8, .108*height, 16, .08*height, '#c52f35', 'A'),
             (x-8, .195*height, 16, .61*height, '#c52f35', 'B'),
             (.16*width, .84*height, .82*width, .09*height, '#087b8d', 'C')]
    for bx, by, bw, bh, color, label in boxes:
        ax.add_patch(Rectangle((bx,by),bw,bh,fill=False,edgecolor=color,linewidth=2))
        ax.text(bx+bw+5, by+12, label, color=color, weight='bold', fontsize=13,
                bbox=dict(facecolor='white',edgecolor=color,pad=2))
    note = fig.add_axes([width/(width+480)+.018,.03,440/(width+480),.94])
    note.axis('off')
    note.text(0,.98, f'Example {i}: annotated IGV evidence', fontsize=16, weight='bold', va='top')
    descriptions = [
        f'{candidate["chrom"]}:{candidate["pos"]:,}\nExact allele: '+str(candidate.get('ref',''))+' > '+str(candidate.get('alt','')),
        'A — Five-sample genotype column\nThe boxed column is the selected locus.\nEach row is one sample; read its genotype\nwith the numerical table in the report.',
        'B — Evidence in all five BAMs\nThe vertical rectangle follows this same\nreference position through the five read\nand coverage tracks. Compare alternate\nbases or insertion marks across samples.',
        'C — Reference and transcript context\nThe lower rectangle identifies the reference\nsequence and nearby transcript models.\nAn overlapping model is not itself proof\nof a functional effect.',
        'How to read the evidence\nPink/purple read backgrounds encode strand,\nnot genotype. Colored base columns mark\nmismatches; insertion indicators mark indels.\nUse AD/DP and pileups to quantify support.',
        'Interpretation\nThis allele is retained in both controls\nand all three CRIS samples. It illustrates\na predicted consequence, not a demonstrated\nCRIS-specific mutation or causal effect.',
        'Reproducible overlay only\nRectangles and this sidebar are added to an\nunaltered IGV screenshot. The original is\nlinked separately for independent inspection.'
    ]
    for y, text in zip([.91,.80,.65,.48,.33,.18,.05], descriptions):
        note.text(0,y,text,fontsize=10,va='top',linespacing=1.35)
    output = root/f'png/10_annotated_candidate_{i}.png'
    fig.savefig(output, dpi=100)
    plt.close(fig)
    manifest.append({'source':str(source.relative_to(root)), 'output':str(output.relative_to(root)),
                     'locus':f'{candidate["chrom"]}:{candidate["pos"]}',
                     'boxes_pixels':boxes})
(root/'provenance/igv-callout-coordinates.json').write_text(json.dumps(manifest,indent=2)+'\n')
