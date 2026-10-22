"""Add a narrow locus rectangle to actual screenshots; retain originals."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

p=argparse.ArgumentParser()
p.add_argument('--output',type=Path,default=Path('output'))
a=p.parse_args()
for i in (1,2):
    path=a.output/'igv'/f'example_{i}.png'
    pixels=plt.imread(path)
    h,w=pixels.shape[:2]
    fig=plt.figure(figsize=(w/100,h/100),dpi=100)
    ax=fig.add_axes([0,0,1,1])
    ax.imshow(pixels);ax.set_xlim(0,w);ax.set_ylim(h,0);ax.axis('off')
    # IGV's saved 82-base viewport places the selected position at this column.
    ax.add_patch(Rectangle((w*.575-8,130),16,h-180,fill=False,edgecolor='#cc2936',linewidth=2))
    fig.savefig(a.output/'igv'/f'example_{i}.boxed.png',dpi=100)
    plt.close(fig)
