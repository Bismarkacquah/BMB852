"""Write the Week 8 report from measured outputs after all stages succeed."""
import csv
import hashlib
import json
from pathlib import Path
from statistics import median

root = Path(__file__).resolve().parents[1]
r = root / 'results'
comparison = json.loads((r / 'comparison_summary.json').read_text())
effects = json.loads((r / 'effect_summary.json').read_text())
coverage = json.loads((r / 'coverage_comparison.json').read_text())['samples']
selected = json.loads((r / 'igv_selected_variants.json').read_text())
products = json.loads((r / 'selected_gene_products.json').read_text()) if (r / 'selected_gene_products.json').exists() else {}
distributions = json.loads((r / 'plot_data.json').read_text())['distributions']
with (root / 'samples.tsv').open(encoding='utf-8-sig') as handle:
    metadata = list(csv.DictReader(handle, delimiter='\t'))
assert len(metadata) == 5 and len(effects['samples']) == 5
read_subsets = {}
for row in metadata:
    run = row['run_accession']
    manifest_path = root / f'samples/{run}/raw/download.json'
    if not manifest_path.exists() and run == 'ERR8982185':
        manifest_path = root.parent / 'Week-7/expanded/provenance/download.json'
    read_subsets[run] = json.loads(manifest_path.read_text())
(root / 'provenance/read-subsets.json').write_text(json.dumps(read_subsets, indent=2) + '\n')
images = ['01_sample_variant_counts.png', '02_quality_depth.png', '03_predicted_impacts.png', '04_observed_call_overlap.png', '05_five_sample_genotypes.png', '07_regional_coverage.png']
images += [f'06_candidate_{i}.png' for i in range(1, len(selected)+1)]
images += ['08_all_merged_variants.png', '09_all_call_patterns.png']
images += [f'10_annotated_candidate_{i}.png' for i in range(1, len(selected)+1)]
for filename in images:
    path = root / 'png' / filename
    assert path.is_file() and path.stat().st_size > 1000, f'Missing/empty image: {path}'
    assert path.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n', f'Not a PNG: {path}'

lines = ['# Week 8  -  five-sample variant analysis', '',
         '## Sequencing Data and Reference Genome', '',
         '| Sequence information | Accession or description |', '|---|---|',
         '| Organism | *Physcomitrium patens* (moss) |',
         '| Sequencing study / BioProject | [PRJEB51295](https://www.ebi.ac.uk/ena/browser/view/PRJEB51295) |',
         '| Reference genome assembly | [GCA_000002425.2](https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000002425.2/) |',
         '| Reference assembly name | Phypa V3 |',
         '| Reference sequence length | 471,852,792 bp |',
         '| Sequencing data | Paired-end whole-genome sequencing (WGS), five runs |',
         '| Analyzed subset | First 20 million read pairs per run, 100 million pairs across five runs |', '',
         '**Accession reminder:** The sequencing-run identifiers for these samples begin with **ERR**. They serve the same role as the **SRR** run numbers used in other datasets. **PRJEB** identifies the study, **GCA** identifies the assembled reference genome, **ERX** identifies an experiment, and **SAMEA** identifies a biological sample. Use the ERR run accessions below to retrieve the sequencing reads; the GCA accession identifies the reference used for alignment and annotation.', '',
         'I extended the Week 7 *Physcomitrium patens* analysis from one sample to five: the original CRIS1#1 sample plus four additional samples from study **PRJEB51295**. Each new sample was processed independently against the same reference, **GCA_000002425.2_Phypa_V3**, before merging and predicting transcript effects.', '',
         '| Sample | Sequencing run (ERR) | Experiment (ERX) | BioSample (SAMEA) |', '|---|---|---|---|']
for row in metadata:
    run = row['run_accession']
    title = row['sample_title'] + (' · original Week 7' if run == 'ERR8982185' else '')
    lines.append(f'| {title} | [{run}](https://www.ebi.ac.uk/ena/browser/view/{run}) | {row["experiment_accession"]} | {row["sample_accession"]} |')
lines += ['', 'The first **20 million paired records per run** were used, matching the expanded Week 7 analysis. This is deterministic prefix sampling, not random sampling or the full runs. At this setting, the independently processed Week 7 CRIS1#1 VCF/BAM were reused; the other four samples were downloaded and processed separately. The same matching reference FASTA and GFF3 were used for annotation.', '',
          '> **Final merged file:** [five_samples.annotated.vcf.gz](results/five_samples.annotated.vcf.gz) · [Tabix index](results/five_samples.annotated.vcf.gz.tbi) · [five sample IDs](results/merged_samples.txt)', '',
          '**Reproduce the analysis:** [chronological commands and every analytical option explained](CODE_GUIDE.md) · [Makefile](Makefile) · [software environment](environment.yml) · [IGV batch](igv/five_samples.batch.txt) · [IGV session](igv/five_samples.session.xml)', '',
          '## Results', '', '### 1. Five separate callsets → one multisample VCF', '',
          '| Sample | PASS records | SNPs | Indels | Median DP | Median QUAL |', '|---|---:|---:|---:|---:|---:|']
names = {m['run_accession']: m['sample_title'] for m in metadata}
for row in comparison['sample_counts']:
    run = row['sample']
    lines.append(f'| {names[run]} | {row["pass_records"]:,} | {row["snps"]:,} | {row["indels"]:,} | {median(distributions[run]["depth"]):.1f} | {median(distributions[run]["qual"]):.2f} |')
lines += ['', f'The merged VCF contains **{comparison["union_records"]:,} distinct allele records**: **{comparison["union_snp_records"]:,} SNP records** and **{comparison["union_indel_records"]:,} indel records**. The workflow verified the exact union of all five input callsets, the sample-column order, and every carried genotype. There are **{comparison["observed_in_all_five"]:,} allele records retained in all five samples**.', '',
          '![Independent SNP and indel counts](png/01_sample_variant_counts.png)', '',
          '![Quality and usable-depth distributions](png/02_quality_depth.png)', '',
          'The allele-union check compares REF/ALT case-insensitively: the soft-masked reference produces some lowercase input alleles, while BCFtools merge writes uppercase. Letter case does not define a different biological variant. All sample genotypes were checked against their corresponding input calls.', '',
          'The boxplots show PASS-site distributions; outliers are hidden only in the display. These are variant-site depths, not genome-wide average coverage.', '',
          '### 2. Alignment and genome coverage', '',
          '| Sample | Primary mapped | Reference covered | Mean reference depth |', '|---|---:|---:|---:|']
for row in coverage:
    mapped = f'{row["primary_mapped_percent"]:.2f}%' if row['primary_mapped_percent'] is not None else 'not available'
    lines.append(f'| {names[row["sample"]]} | {mapped} | {row["percent_reference_covered"]:.2f}% | {row["genome_mean_depth"]:.3f}× |')
lines += ['', 'Coverage was measured with `samtools coverage -q 20 -Q 0`, using the full FASTA length as the denominator, including uncovered sequence. Mapping percentages are from primary alignment records in flagstat. The coverage command differs from the Week 7 `samtools depth` implementation; compare the definitions as well as the values. See [coverage measurements](results/coverage_comparison.tsv).', '',
          '### 3. Observed overlap and missing calls', '',
          '![Observed PASS callset overlap](png/04_observed_call_overlap.png)', '',
          'Each colored dot marks a retained PASS call in that sample. Gray means no retained call at that allele; it does **not** establish reference genotype. The plot shows the twelve largest observed patterns. Independent variant-only callsets cannot support treatment-specific absence claims without a shared callable-site analysis or genotyping at common sites.', '',
          '### 4. Predicted transcript effects', '',
          'SnpEff uses a custom database built from the matching moss FASTA and GFF. The final merged VCF retains all five sample columns and adds `INFO/ANN` transcript annotations.', '',
          'NCBI transcript identifiers contain literal pipe characters. These delimiters are percent-encoded as `%7C` inside `ANN` Feature_ID values, and every annotation is validated to contain exactly 16 fields, preserving the correct HGVS and warning columns. The source transcript identifiers are retained.', '',
          'NCBI GFF pseudogene features and `pseudo=true` attributes are also used to label the corresponding ANN transcript biotype as `pseudogene`. The selected functional examples below use protein-coding transcript models.', '',
          '| Most severe predicted impact per record | Records |', '|---|---:|']
for impact in ('HIGH', 'MODERATE', 'LOW', 'MODIFIER'):
    lines.append(f'| {impact} | {effects["per_record_most_severe_impact"].get(impact, 0):,} |')
lines += ['', f'Annotations were present for **{effects["annotated_records"]:,} / {effects["records"]:,} records**. Counts above assign one most severe impact to each record; [all transcript annotations](results/variant_effects.tsv) can contain several rows per variant.', '',
          f'Among records with HIGH annotations, **{effects.get("high_impact_records_by_biotype", {}).get("protein_coding", 0):,}** include a protein-coding transcript and **{effects.get("high_impact_records_by_biotype", {}).get("pseudogene", 0):,}** include a pseudogene transcript. Categories can overlap when a record has multiple annotations. A pseudogene consequence is not evidence of a functional protein change.', '',
          '![Predicted impact counts](png/03_predicted_impacts.png)', '',
          'The database was built without separate CDS/protein FASTA validation (`-noCheckCds -noCheckProtein`). Predicted impacts depend on transcript models and are not experimentally established effects. Annotation warnings are retained in [effect_summary.json](results/effect_summary.json).', '',
          '### 5. Five-sample IGV visualization', '',
          'The first image shows the merged genotype track with five sample rows and nearby transcript models. The following close-ups load all five indexed BAMs, the same reference, and the annotated multisample VCF. Read backgrounds are colored by strand; mismatch bases and indel markers should be evaluated alongside the reference and coverage.', '',
          '![Five samples in the merged genotype track](png/05_five_sample_genotypes.png)', '']
for i, c in enumerate(selected, 1):
    lines += [f'#### Example {i}: {c["chrom"]}:{c["pos"]:,} · {c["ref"]}>{c["alt"]}', '',
              f'**Predicted {c["impact"]}: `{c["effect"]}`** · gene `{c["gene"] or "not assigned"}` · transcript `{c["transcript"] or "not assigned"}`.', '',
              f'HGVS coding change: `{c["hgvs_c"] or "not supplied"}`; protein change: `{c["hgvs_p"] or "not supplied"}`. Annotation warning: `{c["warning"] or "none on this selected annotation"}`.', '',
              f'NCBI transcript product: **{products.get(c["transcript"], "not supplied in GFF")}**. A hypothetical-protein label does not assign a biochemical function.', '',
              '| Sample | Original GT | Usable DP | AD (REF,ALT) | Original QUAL |', '|---|---|---:|---|---:|']
    for run, call in c['calls'].items():
        if call is None:
            lines.append(f'| {names[run]} | missing |  -  |  -  |  -  |')
        else:
            lines.append(f'| {names[run]} | `{call["gt"]}` | {call["dp"]} | `{",".join(map(str, call["ad"]))}` | {call["qual"]:.2f} |')
    explanations = {
        'frameshift_variant': 'The annotated indel changes the coding reading frame in this transcript; the predicted downstream protein sequence can therefore change.',
        'stop_gained': 'The annotation predicts a new premature stop codon in this transcript, which could shorten its protein product.',
        'start_lost': 'The annotation predicts a change to the annotated translation-initiation codon. Whether an alternative start is used requires additional evidence.',
        'missense_variant': 'The annotation predicts an amino-acid substitution. This classification alone does not establish whether protein function changes.',
        'synonymous_variant': 'The annotation predicts a coding change without an amino-acid substitution in this transcript.',
        'inframe_insertion': 'The annotation predicts inserted coding bases that preserve the downstream reading frame.',
        'inframe_deletion': 'The annotation predicts deleted coding bases that preserve the downstream reading frame.',
        'splice_acceptor_variant': 'The annotation places the variant at a splice acceptor; an effect on actual RNA splicing needs additional evidence.',
        'splice_donor_variant': 'The annotation places the variant at a splice donor; an effect on actual RNA splicing needs additional evidence.'}
    meaning = next((explanations[e] for e in c['effect'].split('&') if e in explanations),
                   'This is a transcript-context prediction; the effect name and impact must be interpreted with the annotation model and read evidence.')
    lines += ['', meaning, '', f'![Five BAMs at example {i}](png/06_candidate_{i}.png)', '',
              f'This locus met the documented moderate-depth and alternate-support criteria in {len(c["supported_samples"])} sample(s). These measurements support prioritizing the locus for review; they do not by themselves prove causation. Check both read directions, read placement, local alignment context, and the separately saved [per-sample pileups](results/pileups/) before interpreting it.', '']
lines += ['#### Regional view', '', '![Five-sample regional coverage and read alignments](png/07_regional_coverage.png)', '',
          'The regional view spans 5 kb around the first selected example and provides context for nearby coverage changes and calls. Its coverage tracks may autoscale independently, so compare numeric depths rather than apparent bar heights alone. All snapshots are actual IGV output; no illustrative read pileups were substituted.', '',
          'Genomic REF/ALT alleles use the forward reference strand. Coding HGVS notation follows the transcript strand, so negative-strand genes can show complementary base letters.', '',
          '## Reproduce in chronological order', '',
          'The complete commands, line-by-line option explanations, expected outputs, and full source links are in [CODE_GUIDE.md](CODE_GUIDE.md). From this folder, the main steps are:', '',
          '```bash\nconda env create -f environment.yml\nconda activate bmmb852-week8\nmake setup-reference\nmake setup-annotation\nmake test\nmake all\nmake report\n```', '',
          '`make all` independently processes the selected samples, merges, annotates, and summarizes. `make report` adds quantitative comparisons, reference coverage, figures, actual IGV snapshots, and this measured report. A working graphical display and IGV installation are required for its snapshot stage. On this workstation set `IGV_DIR=/opt/IGV_Linux_2.19.8`; elsewhere point it to your local IGV installation.', '',
          '## Discussion and limits', '',
          'This analysis compares retained variants and predicts their transcript consequences using the same reference as Week 7. Differences in call counts can arise from coverage, library properties, alignment quality, or filtering as well as biological variation. Prefix sampling is not random, and a haploid calling model was inferred rather than measured separately for each sample.', '',
          'The selected control/CRIS sample groups are unbalanced. Neither their study labels nor the presence of a predicted HIGH-impact call proves an effect of CRISPR editing. Missing genotypes remain unknown. Candidate interpretation needs read-level review and, for causal claims, additional experimental evidence.', '',
          'IGV images were generated programmatically and checked for valid, nonempty PNG files. Their existence alone does not establish visual review or biological validation; inspect the figures and reopen the saved session to review the evidence.', '',
          '## Provenance and references', '',
          '- [Sample metadata](samples.tsv), [ENA metadata archive](provenance/study-runs.tsv), and [verified fifth sample](provenance/fifth-sample-verified.tsv).',
          '- [Archived read-subset manifests](provenance/read-subsets.json), including source URLs, mate synchronization hashes, selected counts, and downloaded-file hashes.',
          '- [Merge checksums](provenance/merged.sha256), [tool versions](provenance/all-tool-versions.txt), [SnpEff software hashes](provenance/snpeff-software.sha256), and [pipeline status](provenance/pipeline-status.json).',
          '- [Week 8 assignment](https://www.biostarhandbook.com/courses/2026/appbio/variants/variant-effect-prediction-assignment/); workflow requirements supplied in chat because the course page requires login.',
          '- [BCFtools](https://samtools.github.io/bcftools/bcftools.html), [SnpEff database construction](https://pcingola.github.io/SnpEff/snpeff/build_db/), and [IGV batch documentation](https://igv.org/doc/desktop/UserGuide/tools/batch/).', '']
insert = ['## Whole merged VCF overview', '',
          'Every merged allele record and all 31 observed call patterns are visualized in the [whole-VCF analysis](results/WHOLE_VCF_ANALYSIS.md). It includes all 214 contigs with calls, pairwise retained-call similarity, and interpretation of shared versus missing calls.', '',
          '![All five samples: callset similarity and every call pattern](png/09_all_call_patterns.png)', '',
          'The three IGV examples have alternate calls in both controls and all three CRIS samples; they do not distinguish treatment groups. Shared calls can reflect differences from the chosen reference. Sample-specific missing entries require common-site genotyping before biological absence can be inferred.', '']
at = lines.index('## Results')
lines[at:at] = insert
lines[2:2] = ['**Detailed interpretation:** [what every result means, with boxed IGV screenshots](RESULTS_EXPLAINED.md).', '']
lines[2:2] = ['**Start here to reproduce:** [setup, quick figure reproduction, full read processing, IGV, and verification](REPRODUCE.md).', '']
for i in range(1, len(selected)+1):
    original = f'![Five BAMs at example {i}](png/06_candidate_{i}.png)'
    if original in lines:
        at = lines.index(original)
        lines[at:at+1] = [f'![Annotated five-BAM evidence at example {i}](png/10_annotated_candidate_{i}.png)', '',
            '**A  -  Genotype column:** The boxed column marks the selected allele across five sample rows. Read the sample genotypes alongside the numerical table above.', '',
            '**B  -  Read evidence:** The vertical rectangle follows the same reference position through all five BAM and coverage tracks. Compare mismatch bases or insertion markers at this position. Pink/purple read backgrounds indicate strand, while AD and DP quantify usable allele support.', '',
            '**C  -  Reference and transcript context:** The lower rectangle identifies the reference sequence and nearby transcript models. Transcript overlap provides annotation context; it does not independently establish a functional effect.', '',
            '**Interpretation:** Both controls and all three CRIS samples retain this alternate allele. It illustrates a predicted transcript consequence, without establishing a CRIS-specific mutation or causal effect.', '',
            f'[Original unannotated screenshot](png/06_candidate_{i}.png) · [Detailed interpretation](RESULTS_EXPLAINED.md). Rectangles are added to the original IGV output; the underlying data are unchanged.']
(root / 'README.md').write_text('\n'.join(lines))
gallery = ['# Week 8 figures', '', 'Generated from the completed five-sample analysis. See the [main report](../README.md) for measurements and interpretation.', '',
           '| Figure | Content |', '|---|---|',
           '| [01](01_sample_variant_counts.png) | Independent SNP and indel counts |',
           '| [02](02_quality_depth.png) | Variant-site depth and quality distributions |',
           '| [03](03_predicted_impacts.png) | Most severe predicted effect per record |',
           '| [04](04_observed_call_overlap.png) | Observed PASS-call overlap |',
           '| [05](05_five_sample_genotypes.png) | Actual IGV merged five-sample genotype track |']
gallery += [f'| [06.{i}](06_candidate_{i}.png) | Actual IGV read evidence at candidate {i} |' for i in range(1, len(selected)+1)]
gallery += ['| [07](07_regional_coverage.png) | Actual IGV regional view with five BAMs |', '']
gallery += ['| [08](08_all_merged_variants.png) | Every merged allele across all contigs with calls |', '| [09](09_all_call_patterns.png) | All call patterns and pairwise retained-call similarities |', '']
gallery += [f'| [10.{i}](10_annotated_candidate_{i}.png) | Boxed IGV locus; explanations appear below the figure in the report |' for i in range(1, len(selected)+1)]
(root / 'png/README.md').write_text('\n'.join(gallery))
hashes = []
for path in [r / 'five_samples.annotated.vcf.gz', *[root / 'png' / filename for filename in images]]:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b''):
            digest.update(chunk)
    hashes.append(f'{digest.hexdigest()}  {path.relative_to(root).as_posix()}')
(root / 'provenance/final-deliverables.sha256').write_text('\n'.join(hashes) + '\n')
print('Wrote measured Week 8 README, validated image files, and final deliverable hashes')
