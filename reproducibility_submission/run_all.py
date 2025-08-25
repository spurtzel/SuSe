#!/usr/bin/env python3

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Optional


RUNS_ROOT = Path('runs')

IGNORE_DIR_RE = re.compile(
    r'(?:^|/)(?:\.git|__pycache__|.*_old.*|old$|empty$|REmatch-no-output(?:/|$))(?:/|$)'
)

PLOT_PATTERNS = (
    '*plot*.py',
    '*lineplot*.py',
    '*boxplot*.py',
    'statesummary_efficiency.py',
    'statesummary_throughputgain.py',
)

FIGURE_MAP_BY_DIR: dict[str, str] = {
    'effectiveness/changing_summary_time_window_sizes': 'Figure6a_changing_summary_time_window_sizes',
    'effectiveness/changing_probability_distribution'  : 'Figure6b_changing_probability_distribution',
    'effectiveness/ablation_study'                     : 'Figure7a_ablation_study',
    'sensitivity_analysis/changing_number_of_eval_timestamps'      : 'Figure8a_changing_number_of_eval_timestamps',
    'sensitivity_analysis/changing_query_length'                   : 'Figure8b_changing_query_length',
    'sensitivity_analysis/changing_number_of_kleene_operators'     : 'Figure8c_changing_number_of_kleene_operators',
    'sensitivity_analysis/positional_kleene'                       : 'Figure8d_positional_kleene',
    'sensitivity_analysis/changing_number_of_disjunction_operators': 'Figure8e_changing_number_of_disjunction_operators',
    'sensitivity_analysis/overlapping_characters'                  : 'Figure8f_overlapping_characters',
    'efficiency/memory_experiment'                                 : 'Figure10d_memory_experiment',
}

FIGURE_MAP_BY_PDF: dict[str, dict[str, str]] = {
    'effectiveness/recall/total_detected_matches': {
        'total_matches_ratio_recall_stream_size_2000.pdf' : 'Figure7b_total_matches_ratio_recall_stream_size_2000',
        'detected_matches_recall_stream_size_2000.pdf'    : 'Figure7c_detected_matches_recall_stream_size_2000',
    },
    'efficiency/flink_core_rematch': {
        'suse_vs_rematch_vs_core_vs_flinkcep.pdf'         : 'Figure9a_suse_vs_rematch_vs_core_vs_flinkcep',
        'throughput_gain_over_rematch_core_flinkcep.pdf'  : 'Figure9b_throughput_gain_over_rematch_core_flinkcep',
    },
    'efficiency/runtime_summary_size_time_window_size': {
        'execution_time_summary_time_window_comparison.pdf': 'Figure10a_execution_time_summary_time_window_comparison',
        'throughput_boxplot.pdf'                           : 'Figure10b_throughput_boxplot',
        'latency_boxplot.pdf'                              : 'Figure10c_latency_boxplot',
    },
    'real_world_experiments/citi_bike': {
        'CitiBike_queries.pdf'               : 'Figure11a_CitiBike_queries',
        'CitiBike_throughput_lineplot.pdf'   : 'Figure11b_CitiBike_throughput_lineplot',
        'CitiBike_latency_lineplot.pdf'      : 'Figure11c_CitiBike_latency_lineplot',
    },
    'real_world_experiments/NASDAQ': {
        'NASDAQ_queries.pdf'                 : 'Figure12a_NASDAQ_queries',
        'NASDAQ_throughput_lineplot.pdf'     : 'Figure12b_NASDAQ_throughput_lineplot',
        'NASDAQ_latency_lineplot.pdf'        : 'Figure12c_NASDAQ_latency_lineplot',
    },
}

PARALLEL_GROUPS: list[set[str]] = [
    {
        'real_world_experiments/citi_bike/query0',
        'real_world_experiments/citi_bike/query1',
    },
    {
        'effectiveness/ablation_study',
        'effectiveness/ablation_study/present_only',
    },
    {
        'effectiveness/recall/total_detected_matches',
        'effectiveness/recall/total_detected_matches_present_only',
    }
]

def sha256sum(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def category_of(rel: Path) -> str:
    return rel.parts[0] if rel.parts else 'other'

def run_stream(cmd: str, cwd: Path, log_file: Path, env=None) -> int:
    cwd.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'w', encoding='utf-8', buffering=1) as log:
        log.write(f"$ {cmd}\n\n")
        p = subprocess.Popen(
            ['/bin/bash', '-lc', cmd],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        for line in p.stdout:
            sys.stdout.write(line)
            log.write(line)
        return p.wait()

class BgProc:
    def __init__(self, proc: subprocess.Popen, log_handle, rel: Path, runner_name: str):
        self.proc = proc
        self.log_handle = log_handle
        self.rel = rel
        self.runner_name = runner_name
    def wait(self) -> int:
        rc = self.proc.wait()
        try:
            self.log_handle.flush()
            self.log_handle.close()
        except Exception:
            pass
        return rc

def run_background(cmd: str, cwd: Path, log_file: Path, env=None) -> BgProc:
    cwd.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log = open(log_file, 'w', encoding='utf-8')
    log.write(f"$ {cmd}\n\n")
    log.flush()
    proc = subprocess.Popen(
        ['/bin/bash', '-lc', cmd],
        cwd=str(cwd),
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    return BgProc(proc, log, Path(cwd), cmd)

def group_priority(rel: Path) -> int:
    s = rel.as_posix()
    if s.startswith('sensitivity_analysis/'): return 0
    if s.startswith('effectiveness/'): return 1
    if s.startswith('real_world_experiments/'): return 3
    if s.startswith('efficiency/'): return 2
    return 4

def present_first_key(rel: Path) -> tuple:
    s = rel.as_posix().lower()
    present_score = 0 if 'present_only' in s else 1
    return (group_priority(rel), present_score, s)

def choose_runner(dpath: Path, root: Path) -> Optional[Path]:
    if dpath.as_posix().startswith('efficiency/flink_core_rematch/'):
        if dpath.as_posix() != 'efficiency/flink_core_rematch':
            return None
    candidates = [
        dpath / 'evaluation_script.sh',
        dpath / 'evaluation_script_suse.sh',
        dpath / 'run_efficiency_experiments.sh',
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def discover_experiments(root: Path):
    exps = []
    for d, _, _ in os.walk(root):
        dpath = Path(d)
        if dpath == root:
            continue
        rel = dpath.relative_to(root)
        srel = rel.as_posix()
        if IGNORE_DIR_RE.search('/' + srel):
            continue
        runner = choose_runner(rel, root)
        if runner:
            exps.append((rel, runner))
    exps.sort(key=lambda x: present_first_key(x[0]))
    return exps

def discover_plot_scripts_for_dir(exp_dir: Path):
    scripts = []
    for cd in (exp_dir, exp_dir / 'plot', exp_dir / 'plots'):
        if not cd.exists(): continue
        for pat in PLOT_PATTERNS:
            scripts.extend(sorted(cd.glob(pat)))
    seen = set(); out = []
    for p in scripts:
        key = str(p.resolve())
        if key in seen: continue
        seen.add(key); out.append(p)
    return out

def copy_reports(src_dir: Path, dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for src in sorted(src_dir.glob('report*.csv')):
        if 'old' in src.name.lower():
            continue
        target = dest_dir / src.name
        shutil.copy2(src, target)
        copied.append(target)
    for name in ('output.log', 'nohup.out'):
        s = src_dir / name
        if s.exists():
            shutil.copy2(s, dest_dir / name)
    return copied

def run_plots(exp_dir: Path, logs_dir: Path):
    env_plot = os.environ.copy()
    env_plot['MPLBACKEND'] = 'Agg'
    plot_scripts = discover_plot_scripts_for_dir(exp_dir)
    if not plot_scripts:
        return
    tag = exp_dir.as_posix().replace('/', '__')
    for ps in plot_scripts:
        ps_rel = ps.relative_to(exp_dir)
        print(f"Plotting: {exp_dir.as_posix()} -> {ps_rel}")
        rc = run_stream(
            f"python3 '{ps.name}'",
            cwd=ps.parent,
            log_file=logs_dir / f"{tag}_plot_{ps.stem}.log",
            env=env_plot
        )
        if rc != 0:
            print(f"WARNING: plot failed for {exp_dir.as_posix()}/{ps.name} (exit {rc}).")

def list_generated_pdfs(exp_dir: Path) -> list[Path]:
    out: set[Path] = set()
    for d in (exp_dir, exp_dir / 'plot', exp_dir / 'plots'):
        if d.exists():
            out |= {p.resolve() for p in d.glob('*.pdf')}
    return sorted(out)

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def pdfunite_with_retry(base: Path, produced: Path, out_path: Path, cwd: Path, logs_dir: Path, tag: str, attempts: int = 3, delay: float = 0.5) -> int:
    base = Path(base).resolve()
    produced = Path(produced).resolve()
    out_path = Path(out_path).resolve()

    cmd = f"pdfunite '{base}' '{produced}' '{out_path}'"
    for k in range(1, attempts + 1):
        rc = run_stream(cmd, cwd=cwd, log_file=logs_dir / f"{tag}_pdfunite_{produced.stem}_{k}.log")
        if rc == 0 and out_path.exists() and out_path.stat().st_size > 0:
            return 0
        time.sleep(delay)
    return 1



def make_side_by_side_pdf(left_pdf: Path, right_pdf: Path, out_pdf: Path,
                          title_left="paper plot", title_right="reproduced plot",
                          dpi: int = 600):
    import tempfile
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import subprocess

    tmpdir = Path(tempfile.mkdtemp(prefix="sbs_"))
    left_png  = tmpdir / "left.png"
    right_png = tmpdir / "right.png"

    def _to_png(pdf_path: Path, out_png: Path, dpi: int):
        subprocess.run([
            'pdftoppm',
            '-r', str(dpi),
            '-png',
            '-singlefile',
            str(pdf_path),
            str(out_png.with_suffix(''))
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    _to_png(left_pdf, left_png, dpi)
    _to_png(right_pdf, right_png, dpi)

    img_l = plt.imread(str(left_png))
    img_r = plt.imread(str(right_png))

    h_l, w_l = img_l.shape[:2]
    h_r, w_r = img_r.shape[:2]
    h_px = max(h_l, h_r)
    w_px = w_l + w_r

    fig_w_in = w_px / dpi
    fig_h_in = h_px / dpi

    fig = plt.figure(figsize=(fig_w_in, fig_h_in))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(img_l)
    ax1.axis('off')
    ax1.set_title(title_left)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(img_r)
    ax2.axis('off')
    ax2.set_title(title_right)

    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(str(out_pdf), bbox_inches='tight')
    plt.close(fig)

    try:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass



def copy_pdf_and_derivatives(p: Path, exp_dir: Path, dest_plots: Path, logs_dir: Path):
    ensure_dir(dest_plots)
    target = dest_plots / p.name
    shutil.copy2(p, target)
    base = exp_dir / 'plot_paper_version' / p.name
    if base.exists():
        tag = exp_dir.as_posix().replace('/', '__')
        cmp_out = dest_plots / f"{p.stem}_compare.pdf"
        _ = pdfunite_with_retry(base, target, cmp_out, cwd=exp_dir, logs_dir=logs_dir, tag=tag)
        sbs_out = dest_plots / f"{p.stem}_side_by_side.pdf"
        try:
            make_side_by_side_pdf(base, target, sbs_out, title_left="paper plot", title_right="reproduced plot")
        except Exception as e:
            (dest_plots / f"{p.stem}_side_by_side.ERROR.txt").write_text(str(e), encoding='utf-8')

def copy_filtered_pdfs(pdfs: Iterable[Path], exp_dir: Path, dest_dir: Path, logs_dir: Path, allowed_base_names: Optional[set[str]]):
    plots_out = ensure_dir(dest_dir / 'plots')
    for p in pdfs:
        name = p.name
        if allowed_base_names is not None and name not in allowed_base_names:
            continue
        copy_pdf_and_derivatives(p, exp_dir, plots_out, logs_dir)

def ablation_ready(root: Path) -> bool:
    main = root / 'effectiveness' / 'ablation_study'
    pres = main / 'present_only'
    return (main / 'report.csv').exists() and (pres / 'report_present.csv').exists()

def ablation_copy_present(root: Path):
    main = root / 'effectiveness' / 'ablation_study'
    pres = main / 'present_only'
    src = pres / 'report_present.csv'
    dst = main / 'report_present.csv'
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied ablation present: {src} -> {dst}")

def recall_ready(root: Path) -> bool:
    base = root / 'effectiveness/recall/total_detected_matches'
    pres = root / 'effectiveness/recall/total_detected_matches_present_only'
    return (base / 'report_suse.csv').exists() and (pres / 'report_suse_wo_expected.csv').exists()

def recall_copy_present(root: Path):
    base = root / 'effectiveness/recall/total_detected_matches'
    pres = root / 'effectiveness/recall/total_detected_matches_present_only'
    src = pres / 'report_suse_wo_expected.csv'
    dst = base / 'report_suse_wo_expected.csv'
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied recall present: {src} -> {dst}")

def citi_ready(root: Path) -> bool:
    q0 = root / 'real_world_experiments/citi_bike/query0'
    q1 = root / 'real_world_experiments/citi_bike/query1'
    
    return (q0 / 'report_query_0.csv').exists() and (q1 / 'report_query_1.csv').exists()
    
    
def citi_copy_to_parent(root: Path):
    parent = root / 'real_world_experiments/citi_bike'
    q0_src = root / 'real_world_experiments/citi_bike/query0' / 'report_query_0.csv'
    q1_src = root / 'real_world_experiments/citi_bike/query1' / 'report_query_1.csv'

    if q0_src.exists():
        dst = parent / 'report_query_0.csv'
        shutil.copy2(q0_src, dst)
        print(f"Copied: {q0_src} -> {dst}")
    else:
        print("WARNING: no report_query_0.csv found in query0/")

    if q1_src.exists():
        dst = parent / 'report_query_1.csv'
        shutil.copy2(q1_src, dst)
        print(f"Copied: {q1_src} -> {dst}")
    else:
        print("WARNING: no report_query_1.csv found in query1/")

def should_defer_plot_for_dir(rel: Path) -> bool:
    s = rel.as_posix()
    if s == 'effectiveness/ablation_study':
        return True
    if s == 'effectiveness/recall/total_detected_matches':
        return True
    return False

def figure_dirs_for(rel: Path) -> list[tuple[Path, Optional[set[str]]]]:
    srel = rel.as_posix()
    cat = category_of(rel)
    out: list[tuple[Path, Optional[set[str]]]] = []
    if srel in FIGURE_MAP_BY_PDF:
        mapping = FIGURE_MAP_BY_PDF[srel]
        for pdf_name, fig_name in mapping.items():
            dest = RUNS_ROOT / cat / fig_name
            out.append((dest, {pdf_name}))
        return out
    if srel in FIGURE_MAP_BY_DIR:
        dest = RUNS_ROOT / cat / FIGURE_MAP_BY_DIR[srel]
        out.append((dest, None))
        return out
    dest = RUNS_ROOT / cat / rel.as_posix().replace('/', '__')
    out.append((dest, None))
    return out

def postprocess_and_distribute(rel: Path, logs_dir: Path, figure_done: set[str]):
    srel = rel.as_posix()
    if srel.startswith('effectiveness/recall/'):
        root = Path('.')
        if recall_ready(root):
            recall_copy_present(root)
            main_rel = Path('effectiveness/recall/total_detected_matches')
            if main_rel.as_posix() not in figure_done:
                run_plots(main_rel, logs_dir)
                pdfs = list_generated_pdfs(main_rel)

                for dest, allowed in figure_dirs_for(main_rel):
                    ensure_dir(dest)
                    copy_reports(main_rel, dest)
                    copy_filtered_pdfs(pdfs, main_rel, dest, logs_dir, allowed)

                if pdfs:
                    build_and_store_paper(logs_dir, tag_suffix=main_rel.as_posix().replace('/', '__'))
                print("effectiveness/recall/total_detected_matches: composite plots done.")
                figure_done.add(main_rel.as_posix())

        return
    if srel.startswith('effectiveness/ablation_study'):
        root = Path('.')
        if ablation_ready(root):
            ablation_copy_present(root)
            main_rel = Path('effectiveness/ablation_study')
            if main_rel.as_posix() not in figure_done:
                run_plots(main_rel, logs_dir)
                pdfs = list_generated_pdfs(main_rel)

                for dest, allowed in figure_dirs_for(main_rel):
                    ensure_dir(dest)
                    copy_reports(main_rel, dest)
                    copy_filtered_pdfs(pdfs, main_rel, dest, logs_dir, allowed)

                if pdfs:
                    build_and_store_paper(logs_dir, tag_suffix=main_rel.as_posix().replace('/', '__'))

                print("effectiveness/ablation_study: composite plots done.")
                figure_done.add(main_rel.as_posix())

        return
    if srel.startswith('real_world_experiments/citi_bike/'):
        root = Path('.')
        if citi_ready(root):
            citi_copy_to_parent(root)
            parent_rel = Path('real_world_experiments/citi_bike')
            if parent_rel.as_posix() not in figure_done:
                run_plots(parent_rel, logs_dir)
                pdfs = list_generated_pdfs(parent_rel)

                for dest, allowed in figure_dirs_for(parent_rel):
                    ensure_dir(dest)
                    for pth in (parent_rel / 'report_query_0.csv', parent_rel / 'report_query_1.csv'):
                        if pth.exists():
                            shutil.copy2(pth, ensure_dir(dest) / pth.name)
                    copy_filtered_pdfs(pdfs, parent_rel, dest, logs_dir, allowed)

                if pdfs:
                    build_and_store_paper(logs_dir, tag_suffix=parent_rel.as_posix().replace('/', '__'))

                print("real_world_experiments/citi_bike: composite plots done.")
                figure_done.add(parent_rel.as_posix())

        return
    exp_dir = rel
    if should_defer_plot_for_dir(exp_dir):
        return
    run_plots(exp_dir, logs_dir)
    pdfs = list_generated_pdfs(exp_dir)

    for dest, allowed in figure_dirs_for(exp_dir):
        ensure_dir(dest)
        copied_csv = copy_reports(exp_dir, dest)
        copy_filtered_pdfs(pdfs, exp_dir, dest, logs_dir, allowed)
        print(f" {exp_dir.as_posix()} -> {dest}: {len(copied_csv)} CSV(s) copied.")

    if pdfs:
        build_and_store_paper(logs_dir, tag_suffix=exp_dir.as_posix().replace('/', '__'))

def need_to_run(exp_dir: Path, force: bool) -> bool:
    if force:
        return True
    return not any(exp_dir.glob('report*.csv'))

def run_single(rel: Path, runner_rel: Path, logs_dir: Path, env) -> int:
    exp_dir = rel
    runner = runner_rel
    tag = rel.as_posix().replace('/', '__')
    _ = run_stream(f"chmod +x '{runner.name}'", cwd=exp_dir, log_file=logs_dir / f"{tag}_chmod.log")
    rc = run_stream("set -eo pipefail; './{}'".format(runner.name),
                    cwd=exp_dir,
                    log_file=logs_dir / f"{tag}.log",
                    env=env)
    return rc

def run_parallel(pairs: list[tuple[Path, Path]], logs_dir: Path, env) -> dict[str, int]:
    procs: list[tuple[BgProc, Path]] = []
    results: dict[str, int] = {}
    for rel, runner_rel in pairs:
        tag = rel.as_posix().replace('/', '__')
        _ = run_stream(f"chmod +x '{runner_rel.name}'", cwd=rel, log_file=logs_dir / f"{tag}_chmod.log")
        cmd = "set -eo pipefail; './{}'".format(runner_rel.name)
        proc = run_background(cmd, cwd=rel, log_file=logs_dir / f"{tag}.log", env=env)
        procs.append((proc, rel))
    for proc, rel in procs:
        rc = proc.wait()
        results[rel.as_posix()] = rc
        if rc != 0:
            print(f"FAILED {rel.as_posix()} exit={rc}. See logs.")
    return results

def set_num_runs_in_file(path: Path, value: int) -> bool:
    if not path.exists():
        return False
    txt = path.read_text(encoding='utf-8', errors='ignore')
    pat = re.compile(r'^(\s*NUM_OF_RUNS\s*=\s*)\((?:[^)]*)\)(.*)$', re.MULTILINE)
    new = pat.sub(rf'\1({value})\2', txt)
    if new != txt:
        path.write_text(new, encoding='utf-8')
        print(f"Adjusted NUM_OF_RUNS=({value}) in {path.as_posix()}")
        return True
    return False

def adjust_num_runs(root: Path, extensive: bool):
    sens_root = root / 'sensitivity_analysis'
    if sens_root.exists():
        for child in sorted(sens_root.iterdir()):
            if not child.is_dir():
                continue
            name = child.as_posix()
            scripts = [child / 'evaluation_script.sh', child / 'evaluation_script_suse.sh']
            if 'overlapping_characters' in name or 'changing_number_of_eval_timestamps' in name:
                val = 50
            elif 'changing_number_of_disjunction_operators' in name:
                val = 25 if extensive else 5
            else:
                val = 50 if extensive else 10
            for s in scripts:
                set_num_runs_in_file(s, val)

    eff_map = [
        ('effectiveness/changing_probability_distribution', 25, 25),
        ('effectiveness/changing_summary_time_window_sizes', 50, 10),
        ('effectiveness/ablation_study', 25, 5),
        ('effectiveness/ablation_study/present_only', 25, 5),
    ]
    for rel, big, small in eff_map:
        d = root / rel
        if not d.exists():
            continue
        val = big if extensive else small
        for s in (d / 'evaluation_script.sh', d / 'evaluation_script_suse.sh'):
            set_num_runs_in_file(s, val)

def build_and_store_paper(logs_dir: Path, tag_suffix: Optional[str] = None):
    paper_dir = Path('paper')
    if not paper_dir.exists():
        print(f"NOTE: 'paper' directory not found at {paper_dir}; skipping pdflatex.")
        return

    tag = 'paper__pdflatex' + (f"__{tag_suffix}" if tag_suffix else '')
    rc = run_stream(
        "pdflatex -interaction=nonstopmode summarySelector_sigmod25_cameraReady.tex",
        cwd=paper_dir,
        log_file=logs_dir / f"{tag}.log",
        env=os.environ.copy()
    )
    if rc != 0:
        print(f"WARNING: pdflatex returned {rc}. See {(logs_dir / f'{tag}.log').as_posix()}")

    produced = paper_dir / "summarySelector_sigmod25_cameraReady.pdf"
    original = paper_dir / "summarySelector_sigmod25_cameraReady-paper.pdf"

    dest_original = RUNS_ROOT / "paper_plots.pdf"
    dest_produced = RUNS_ROOT / "paper_plots_reproduced.pdf"


    if original.exists():
        try:
            if dest_original.exists():
                dest_original.unlink()
            shutil.copy2(str(original), str(dest_original))
            print(f"Copied {original} -> {dest_original}")
        except Exception as e:
            print(f"WARNING: failed to move original paper PDF: {e}")
    elif not dest_original.exists():
        print(f"NOTE: original paper PDF not found at {original}")

    if produced.exists():
        try:
            if dest_produced.exists():
                dest_produced.unlink()
            shutil.move(str(produced), str(dest_produced))
            print(f"Moved {produced} -> {dest_produced}")
        except Exception as e:
            print(f"WARNING: failed to move reproduced paper PDF: {e}")
    else:
        print(f"NOTE: reproduced paper PDF not found at {produced}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.', help='repo root')
    ap.add_argument('--force', action='store_true', help='re-run even if report*.csv exist')
    ap.add_argument('--keep-going', action='store_true', help='continue on failure')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--extensive-reproducibility', dest='extensive', action='store_true', help='increase NUM_OF_RUNS per mapping')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)

    adjust_num_runs(root, args.extensive)

    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'

    exps = discover_experiments(Path('.'))
    if not exps:
        print("No experiments found.")
        sys.exit(1)

    exp_map = {rel.as_posix(): (rel, runner) for rel, runner in exps}
    processed: set[str] = set()
    figure_done: set[str] = set()

    total = len(exps)
    i = 0

    while i < total:
        rel, runner_rel = exps[i]
        srel = rel.as_posix()
        i += 1

        if srel in processed:
            continue

        group = None
        for g in PARALLEL_GROUPS:
            if srel in g:
                group = g
                break

        if group is not None:
            group_pairs: list[tuple[Path, Path]] = []
            for member in sorted(group):
                if member not in exp_map:
                    continue
                m_rel, m_runner = exp_map[member]
                if need_to_run(m_rel, args.force):
                    group_pairs.append((m_rel, m_runner))

            if args.dry_run:
                print(f"DRY RUN: would execute (parallel) {sorted(group)}")
                for member in group:
                    processed.add(member)
                for member in group:
                    postprocess_and_distribute(Path(member), RUNS_ROOT / '_logs', figure_done)
                continue

            if group_pairs:
                n_done = len(processed)
                print(f"\n[{n_done+1}-{n_done+len(group_pairs)}/{total} experiments] [GROUP] Running in parallel: {', '.join(p[0].as_posix() for p in group_pairs)}")
                results = run_parallel(group_pairs, logs_dir=ensure_dir(RUNS_ROOT / '_logs'), env=env)

                failed = [k for k, rc in results.items() if rc != 0]
                for member in group:
                    processed.add(member)
                for member in group:
                    postprocess_and_distribute(Path(member), RUNS_ROOT / '_logs', figure_done)
                if failed and not args.keep_going:
                    sys.exit(1)
                continue
            else:
                for member in group:
                    processed.add(member)
                for member in group:
                    postprocess_and_distribute(Path(member), RUNS_ROOT / '_logs', figure_done)
                continue

        tag = rel.as_posix().replace('/', '__')
        n_done = len(processed)
        print(f"\n[{n_done+1}/{total} experiments] {rel.as_posix()} -> {runner_rel.name}")
        processed.add(srel)

        if args.dry_run:
            print("DRY RUN: would execute", runner_rel)
            postprocess_and_distribute(rel, RUNS_ROOT / '_logs', figure_done)
            continue

        if not need_to_run(rel, args.force):
            print(f"Skipping run (report*.csv found). Use --force to re-run.")
            postprocess_and_distribute(rel, RUNS_ROOT / '_logs', figure_done)
            continue

        rc = run_single(rel, runner_rel, logs_dir=ensure_dir(RUNS_ROOT / '_logs'), env=env)
        if rc != 0:
            print(f"FAILED {rel.as_posix()} exit={rc}. See logs.")
            if not args.keep_going:
                sys.exit(rc)

        postprocess_and_distribute(rel, RUNS_ROOT / '_logs', figure_done)

    print("\nAll done. Results organized in ./runs/")

if __name__ == '__main__':
    main()
