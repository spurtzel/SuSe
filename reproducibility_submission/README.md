# SuSe Reproducibility Submission (SIGMOD 2025)

This repository contains the code and scripts to reproduce the experimental results and plots for the paper: **SuSe: Summary Selection for Regular Expression Subsequence Aggregation over Streams.** The instructions below explain the end‑to‑end reproducibility (*single-command*), where results, figures, paper PDFs, and outputs are organized, and information about the experiments.

> Figures and experimental design follow the [SuSe paper](https://dl.acm.org/doi/pdf/10.1145/3725359) (§7; Figures 6-12)

We provide *single‑command* reproducibility with `run_repro.sh`. This script executes all experiments sequentially and compiles: (1) the reproduced paper plots, (2) side-by-side comparisons of the reproduced and original plots, and (3) the paper’s evaluation section generated from the reproduced results. 

For questions or support regarding the reproducibility, contact us at: purtzesc@hu-berlin.de
## 1. Quickstart: one‑command run

We recommend running the reproducibility pipeline as follows:

```bash
git clone https://github.com/spurtzel/SuSe.git

cd SuSe/reproducibility_submission

nohup ./run_repro.sh > repro.out 2>&1 & echo $! > repro.pid
```
- `nohup`: makes sure the process keeps running even if you close the terminal or log out
- `> repro.out`: redirects standard output (echo/print) into the file `repro.out`
- `2>&1`: redirects stderr to the same place as stdout
- `&` at the end: runs the script in the background
- `echo $! > repro.pid`: writes process ID into repro.pid

This makes it easy to monitor progress or terminate the application if needed.

- **Stop reproducibility.** `kill $(cat repro.pid)`
  
- **Resume reproducibility.** Re-run the same command as before. Finished runs are skipped automatically (default). Half-finished runs cannot be continued; to re-run them, delete the corresponding report*.csv file in the experiment directory.
  
- **Monitor progress.** `tail -f repro.out`
  
#### What `./run_repro.sh` does:
- Builds the Docker image `paper-repro:latest` if it is not present.
  
- Downloads the **Citi Bike** trip dataset for the real‑world experiments on the first run and saves
  `202307-citibike-tripdata.csv` under `real_world_experiments/citi_bike/query0/` and `real_world_experiments/citi_bike/query1/`. Existing files are reused on subsequent runs.

  
- Prepares the **FlinkCEP** baseline (used in Fig. 9a–9b). If
  `reproducibility_submission/efficiency/flink_core_rematch/FLINK/flink_cep/java-cep/target/beispiel-1.0-SNAPSHOT.jar`  is missing, the script unpacks it from
  `.../target/beispiel-1.0-SNAPSHOT.jar.tar.gz`. 

- Starts a progress watcher, adjusted by `PROGRESS_PERIOD` (default 600 seconds). The progress watcher prints the progress of the current experiment every 10 minutes. To change the delay, set the `PROGRESS_PERIOD` environment variable (e.g., `PROGRESS_PERIOD=300 nohup ./run_repro.sh ...`). 
	- **Note:** later runs of an experiment often use larger parameter sizes (e.g., summary and time window), which significantly increase runtime.
  
- Runs the orchestrator:
  ```bash
  python3 -u run_all.py
  ```

#### Orchestrator `run_all.py`
 - **Runs & resumes experiments.** Executes experiment directories in the order (1) *sensitivity analysis*, (2) *effectiveness*, (3) *efficiency*, and (4) *real-world experiments*. On a fresh run, the first experiment executed is `sensitivity_analysis/changing_number_of_disjunction_operators`. Skips experiments that already have `report*.csv`, and streams logs to `./runs/_logs/`. 

 - **Post‑processes & organizes.** Runs plot scripts, creates reproduced + comparison PDFs, copies reports into figure‑named directories under `./runs/`, and incrementally rebuilds the reproduced paper PDF (`./runs/paper_plots_reproduced.pdf`) upon finishing an experiment.

#### Monitor progress
Using `tail -f repro.out`, you can stream updates from the `repro.out` file to the console. For instance:

```
[8/18 experiments] effectiveness/changing_probability_distribution -> evaluation_script.sh
[2025-08-18 13:57:20] monitoring: effectiveness/changing_probability_distribution/report.csv
[2025-08-18 13:57:20] [effectiveness/changing_probability_distribution] total runs = 750
[2025-08-18 13:57:20] [effectiveness/changing_probability_distribution] 350 of 750 runs finished ~ 46.7% done
[2025-08-18 14:07:20] [effectiveness/changing_probability_distribution] 550 of 750 runs finished ~ 73.3% done
[2025-08-18 14:17:20] [effectiveness/changing_probability_distribution] 650 of 750 runs finished ~ 86.7% done
[2025-08-18 14:27:20] [effectiveness/changing_probability_distribution] 700 of 750 runs finished ~ 93.3% done
[2025-08-18 14:37:20] [effectiveness/changing_probability_distribution] 700 of 750 runs finished ~ 93.3% done
[2025-08-18 14:47:20] [effectiveness/changing_probability_distribution] 700 of 750 runs finished ~ 93.3% done
[2025-08-18 14:57:20] [effectiveness/changing_probability_distribution] 702 of 750 runs finished ~ 93.6% done
[2025-08-18 15:07:20] [effectiveness/changing_probability_distribution] 725 of 750 runs finished ~ 96.7% done

Plotting: effectiveness/changing_probability_distribution -> probability_distribution_uni_norm_plot.py
 effectiveness/changing_probability_distribution -> runs/effectiveness/Figure6b_changing_probability_distribution: 1 CSV(s) copied.

Transcript written on summarySelector_sigmod25_cameraReady.log.
Moved paper/summarySelector_sigmod25_cameraReady.pdf -> runs/paper_plots_reproduced.pdf
```
- **First message on a fresh run.** After the Docker image has been built and the first experiment starts, the first progress line you should see in `repro.out` is:
  
  `[1/18 experiments] sensitivity_analysis/changing_number_of_disjunction_operators -> evaluation_script.sh`


#### Artifacts  
- Plots, results, and reproduced paper PDFs are stored in `./runs/` (see *§4. What gets produced* for details).
- Logs for experiments, plots, and `pdflatex` are written to `./runs/_logs/`.
- Plots are organized per experiment and also copied into per-figure directories (e.g., `./runs/effectiveness/Figure7a_ablation_study`).

#### Seeds & determinism 
- All randomized components (see *§6. Repository & experiment layout#Workflow*) use fixed seeds to ensure deterministic results for most experiments.

## 2. Requirements (Environment & Hardware)
  
- **Docker workflow.** The user must be able to run `docker` (via `sudo` or by being in the `docker` group ([see here](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user))). Reproducibility is executed inside a Docker image built from the repository’s `Dockerfile` and tagged `paper-repro:latest`. 
  
- **Host system requirements.** A recent **x86_64 Linux** (e.g., Ubuntu 20.04/24.04 LTS, Arch, Debian 12) with **Docker Engine >= 20.10** and internet access to build the image.  We recommend **>= 50 GB** free disk space, **32 GB RAM**, and **>= 4 CPU cores**. No GPU required. Avoid running the container with strict memory caps (e.g., `docker run -m <24 GB>`), as some experiments will OOM.

- **Reproducibility hardware.** We ran the reproducibility on a system with an Intel i7-1265U processor (**10 cores/12 threads; @4.80 GHz**) and **32GB RAM**. 
  
- **Smaller sample sizes.** Experiments can also be run with sample sizes reduced by 80% compared to the paper (see §5 Running options & orchestration). This allows much faster execution while still yielding results and trends close to those in the paper. We especially recommend this option for weaker systems.
  
## 2.1 Docker image overview

- The Docker image is based on `python:3.10-slim` (Debian) with `default-jre-headless` for Java‑based baselines (FlinkCEP, CORE), `poppler-utils`/`ghostscript` for PDF tooling used in plot comparisons, C/C++ runtime libs (`libstdc++6`, `libgomp1`, `libgcc-s1`, `zlib1g`) for compiled components and OpenMP, standard CLI utilities (`bash`, `coreutils`, `procps`, `ca-certificates`, `curl`, `git`, `time`) for experiments/orchestration/logging, **TeX Live (texlive-full)** to run plot scripts and compile the paper with reproduced plots, and Python dependencies from `requirements.txt`.
- You can build the Docker image manually via `docker build -t paper-repro:latest .`

## 2.2 Dataset download (Citi Bike)

`run_repro.sh` downloads the Citi Bike **trip dataset** used in our real‑world experiments. This happens **once** on the first run, before any experiments start. This step requires internet access. 
- **Storage location.** The file `202307-citibike-tripdata.csv` is saved under `real_world_experiments/citi_bike/query0/` and `real_world_experiments/citi_bike/query1/`.
- **Re-use.** If `202307-citibike-tripdata.csv` is already present, it is **not** downloaded again.
  
## 3. How long will it take? (Experiment durations)

In total, the experiments took about **5 days** on our specified hardware with the *smaller* sample sizes. We estimate roughly twice as long when using the larger sample sizes. 

| Experiment Group         | Experiment                               | Figures    | Runtime (approx.)                     |
| ------------------------ | ---------------------------------------- | ---------- | ------------------------------------- |
| **Effectiveness (~30h)** |                                          |            |                                       |
|                          | Changing summary / time window sizes     | Fig. 6a    | **11h**                               |
|                          | Changing probability distribution        | Fig. 6b    | **1.5h**                              |
|                          | Ablation study                           | Fig. 7a    | **16h**                               |
|                          | Recall experiment                        | Fig. 7b,7c | **1.5h**                              |
| **Sensitivity (~5.5h)**  |                                          |            |                                       |
|                          | Changing number of evaluation timestamps | Fig. 8a    | **0.5h**                              |
|                          | Changing pattern length                  | Fig. 8b    | **0.5h**                              |
|                          | Changing number of Kleene operators      | Fig. 8c    | **2h**                                |
|                          | Changing Kleene position                 | Fig. 8d    | **0.5h**                              |
|                          | Changing number of disjunction operators | Fig. 8e    | **1h**                                |
|                          | Changing pattern character overlap       | Fig. 8f    | **1h**                                |
| **Efficiency (~52h)**    |                                          |            |                                       |
|                          | StateSummary / Flink / CORE / REmatch    | Fig. 9a,9b | **2h**                                |
|                          | Execution time, Throughput, Latencies    | Fig. 10a-c | **48h**                               |
|                          | Memory usage                             | Fig. 10d   | **2h**                                |
| **Real-world (~32h)**    |                                          |            |                                       |
|                          | Citi Bike                                | Fig. 11a-c | **28h**                               |
|                          | NASDAQ                                   | Fig. 12a-c | **4h**                                |
| **Total**                | -                                        | -          | **119.5h<br>~5 days (small samples)** |

**Note**
- We also ran parts of the experiments on a **virtual machine (4 cores @ 3GHz, 32GB RAM)**, where execution was approximately **> 2 times slower** per experiment.

## 4. What gets produced? (figures, reports, paper PDFs)

All experiment runs create `report*.csv` files (and selected logs) in per‑figure directories under `./runs/`
- `report*.csv` contains *all* results for an experiment
- Plots (`*.pdf`) are copied into a `plots/` subdirectory (also contains helpful comparison artifacts):
  - `<figure>.pdf` is the *reproduced* plot
  - `<figure>_compare.pdf` concatenation of the original paper plot and reproduced plot (in that order)
  - `<figure>_side_by_side.pdf` a side‑by‑side rasterized comparison of the original paper and reproduced plot

```
     report.csv                     # experiment results 
     plots/
         <figure>.pdf               # reproduced plot
         <figure>_compare.pdf       # pdf paper plot comparison
         <figure>_side_by_side.pdf  # side-by-side paper plot comparison
```

For instance:
```
 ./runs/effectiveness/Figure7a_ablation_study
     report.csv                           # results 
     report_present.csv                   # results 
     plots/
         ablation_study.pdf               # reproduced plot
         ablation_study_compare.pdf       # pdf original paper plot comparison
         ablation_study_side_by_side.pdf  # side-by-side paper plot comparison
```

After *each* experiment, the script also tries to **build the paper PDF** from `paper/summarySelector_sigmod25_cameraReady.tex` using the reproduced plots and moves results into `./runs/`:
- `./runs/paper_plots.pdf`: the original paper plots
- `./runs/paper_plots_reproduced.pdf`: PDF compiled from the current reproducibility state, including all plots from experiments that have successfully completed so far.
  
## 5. Running options & orchestration

### Reproducibility scripts `run_repro.sh` and `run_all.py`

The main orchestrator is `run_repro.sh`, which internally calls `run_all.py`. You can adjust the following start parameters:

```bash
# show options
python3 run_all.py --help

# re-run everything even if reports exist
python3 run_all.py --force

# keep going after a failed experiment
python3 run_all.py --keep-going

# dry run (print what would be executed)
python3 run_all.py --dry-run

# use larger NUM_OF_RUNS where supported (matches paper-scale sampling)
python3 run_all.py --extensive-reproducibility
```

**Notes:**
- If an experiment directory, e.g., `effectiveness/ablation_study`, already contains a `report*.csv` file, the experiment *is not* re-run, but only the plot scripts are executed based on the current `report*.csv` file(s). This also means that a finished experiment *does not* need to be re-run if an error later occurs.
- `--force` re-runs experiments even if a `report*.csv` is available in the directory. 
- By default, `run_repro.sh` uses `--keep-going`.
- `--extensive-reproducibility` adjusts `NUM_OF_RUNS` inside several `evaluation_script*.sh` files to paper‑scale values. **By default, the number of samples is reduced (in comparison to the paper)**.

### Running a single experiment
Each experiment can be run via the executable, e.g., `evaluation_script.sh`, in its corresponding directory. When using Docker, modify the last line of `run_repro.sh` to execute a single experiment:
``` bash
# from
bash -lc "python3 -u run_all.py"

# to, e.g.,
bash -lc "./sensitivity_analysis/changing_number_of_disjunction_operators/evaluation_script.sh"
```
The plot script (e.g., `combined_num_disjunction_operators_plot.py`) is not executed automatically in this case and must be run manually. The resulting plot will be in the same experiment directory.

## 6. Repository & experiment layout
### Repository structure
The repository is organized into four main parts:
 - **Dockerfile & reproducibility scripts**. For setting up and running reproducibility.
 - **Experiment directories**. Contain scripts and configurations per experiment.
 - **LaTeX paper sources**. For reproducing the paper (with reproduced plots).
 - **Results & logs**. Includes experiment outputs, logs, reproduced paper, and original paper.

```
../SuSe/reproducibility_submission
    # dockerfile and reproducibility scripts
	Dockerfile                 # slim Debian, python 3.10, Java, ...
	run_repro.sh               # builds docker image, starts orchestrator
	run_all.py                 # orchestrates experiments, plots, pdfs, ...
	progress_watcher.sh        # prints current experiment progress
	requirements.txt           # python dependencies

    # experiment directories
	effectiveness              # Fig. 6a,b; Fig. 7a-c
	sensitivity_analysis       # Fig. 8a-f
	efficiency                 # Fig. 9a,b; Fig. 10a-d
	real_world_experiments     # Fig. 11a-c; Fig 12a-c
	
    # latex files for compiling the paper with reproduced plots
	paper
	
    # contains experiment results, logs, reproduced paper, original paper, ..
	runs
```

### Experiment directory structure
```text
experiment/
├── evaluation_script.sh
├── run_test.sh
├── evaluation_timestamp_generator.py
├── event_stream_generator.py
├── append_to_report.py
├── summary_selector
├── plot.py
├── plot_paper_version
│   └── paper_plot.pdf
└──  report.csv (after the experiment ran)
```
#### Workflow
- **evaluation_script.sh:** Sets up experiment parameters ([see here](https://github.com/spurtzel/SuSe?tab=readme-ov-file#parameters)) . For each combination of parameters, e.g., regular expression, summary size, time window size, ..., the script calls `run_test.sh`. A fixed random seed is set for each run and propagated downstream, ensuring determinism for most experimental results.
- **run_test.sh:** Orchestrates a single experiment. Generates evaluation timestamps with `evaluation_timestamp_generator.py` and event streams with `event_stream_generator.py` for each parameter configuration and runs SuSe and baselines (e.g., FIFO/Random) via compiled binary `summary_selector` ([see here on compilation](https://github.com/spurtzel/SuSe?tab=readme-ov-file#compilation-steps)) for each strategy. Both generators use fixed seeds as inputs (see `event_stream_generator.py` and `evaluation_timestamp_generator.py`) to ensure determinism.
- **append_to_report.py:** Merges the results from all strategies into `report*.csv`.
- **plot.py:** The original plot script from the paper. The orchestrator runs it after the experiment finished to produce the reproduced plot based on `report*.csv`. Also, comparison artifacts are created based on `plot_paper_version/paper_plot.pdf` (i.e., for each experiment we included the respective paper plot).

### Experimental results directory (`./runs/`) structure

Experimental results are stored under `./runs/` as follows:
```
runs/
  paper_plots.pdf
  paper_plots_reproduced.pdf
  
  _logs/
    <tag>_chmod.log
    <tag>.log
    paper__pdflatex__<tag>.log
    
  effectiveness/
    Figure6a_changing_summary_time_window_sizes/
      report*.csv
      plots/
        <figure>.pdf
        <figure>_compare.pdf
        <figure>_side_by_side.pdf
    Figure7a_ablation_study/
    ...
    
  sensitivity_analysis/
    Figure8a_.../
    ...
    
  efficiency/
    Figure9a_.../
    Figure9b_.../
    Figure10a_.../
    Figure10b_.../
    Figure10c_.../
    Figure10d_memory_experiment/
    
  real_world_experiments/
    Figure11a_.../
    Figure11b_.../
    Figure11c_.../
    Figure12a_.../
    Figure12b_.../
    Figure12c_.../
```


## 7. Figure map

The tables below map each **experiment directory** to its **artifact directory** under `./runs/` and, where relevant, list the **explicit plot PDF** names. Use this to know _where results/artifacts land_. Every artifact directory contains `report*.csv` and `plots/` with `<figure>.pdf` (reproduced), `<figure>_compare.pdf` (original -> reproduced), and `<figure>_side_by_side.pdf`. The mapping mirrors what `run_all.py` uses, so it is also a checklist for verifying that the orchestrator organized results correctly.

All artifact directories below live at `./runs/<experiment_group>/<artifact_dir>/` (e.g., Figure 6a -> `./runs/effectiveness/Figure6a_changing_summary_time_window_sizes/`).

#### Effectiveness
| Figure | Experiment directory                               | Artifact directory name                         |
| :----: | -------------------------------------------------- | ----------------------------------------------- |
|  6a    | `effectiveness/changing_summary_time_window_sizes` | **Figure6a_changing_summary_time_window_sizes** |
|  6b    | `effectiveness/changing_probability_distribution`  | **Figure6b_changing_probability_distribution**  |
|  7a    | `effectiveness/ablation_study`                     | **Figure7a_ablation_study**                     |

#### Effectiveness (Recall)
| Figure | Experiment directory                          | PDF (explicit)                                      | Artifact directory name                                  |
| :----: | --------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------- |
|  7b    | `effectiveness/recall/total_detected_matches` | `total_matches_ratio_recall_stream_size_2000.pdf`   | **Figure7b_total_matches_ratio_recall_stream_size_2000** |
|  7c    | `effectiveness/recall/total_detected_matches` | `detected_matches_recall_stream_size_2000.pdf`      | **Figure7c_detected_matches_recall_stream_size_2000**    |

#### Sensitivity analysis
| Figure | Experiment directory                                            | Artifact directory name                               |
| :----: | --------------------------------------------------------------- | ----------------------------------------------------- |
|  8a    | `sensitivity_analysis/changing_number_of_eval_timestamps`       | **Figure8a_changing_number_of_eval_timestamps**       |
|  8b    | `sensitivity_analysis/changing_query_length`                    | **Figure8b_changing_query_length**                    |
|  8c    | `sensitivity_analysis/changing_number_of_kleene_operators`      | **Figure8c_changing_number_of_kleene_operators**      |
|  8d    | `sensitivity_analysis/positional_kleene`                        | **Figure8d_positional_kleene**                        |
|  8e    | `sensitivity_analysis/changing_number_of_disjunction_operators` | **Figure8e_changing_number_of_disjunction_operators** |
|  8f    | `sensitivity_analysis/overlapping_characters`                   | **Figure8f_overlapping_characters**                   |

#### Efficiency
| Figure | Experiment directory                               | PDF (explicit)                                      | Artifact directory name                                     |
| :----: | -------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------- |
|   9a   | `efficiency/flink_core_rematch`                    | `suse_vs_rematch_vs_core_vs_flinkcep.pdf`           | **Figure9a_suse_vs_rematch_vs_core_vs_flinkcep**            |
|   9b   | `efficiency/flink_core_rematch`                    | `throughput_gain_over_rematch_core_flinkcep.pdf`    | **Figure9b_throughput_gain_over_rematch_core_flinkcep**     |
|  10a   | `efficiency/runtime_summary_size_time_window_size` | `execution_time_summary_time_window_comparison.pdf` | **Figure10a_execution_time_summary_time_window_comparison** |
|  10b   | `efficiency/runtime_summary_size_time_window_size` | `throughput_boxplot.pdf`                            | **Figure10b_throughput_boxplot**                            |
|  10c   | `efficiency/runtime_summary_size_time_window_size` | `latency_boxplot.pdf`                               | **Figure10c_latency_boxplot**                               |
|  10d   | `efficiency/memory_experiment`                     | -                                                   | **Figure10d_memory_experiment**                             |

#### Real‑world experiments
| Figure | Experiment directory               | PDF (explicit)                     | Artifact directory name                    |
| :----: | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
| 11a    | `real_world_experiments/citi_bike` | `CitiBike_queries.pdf`             | **Figure11a_CitiBike_queries**             |
| 11b    | `real_world_experiments/citi_bike` | `CitiBike_throughput_lineplot.pdf` | **Figure11b_CitiBike_throughput_lineplot** |
| 11c    | `real_world_experiments/citi_bike` | `CitiBike_latency_lineplot.pdf`    | **Figure11c_CitiBike_latency_lineplot**    |
| 12a    | `real_world_experiments/NASDAQ`    | `NASDAQ_queries.pdf`               | **Figure12a_NASDAQ_queries**               |
| 12b    | `real_world_experiments/NASDAQ`    | `NASDAQ_throughput_lineplot.pdf`   | **Figure12b_NASDAQ_throughput_lineplot**   |
| 12c    | `real_world_experiments/NASDAQ`    | `NASDAQ_latency_lineplot.pdf`      | **Figure12c_NASDAQ_latency_lineplot**      |

## 8. Experiment descriptions

#### Metrics:
- **Relative recall improvement (higher is better):** At each evaluation point, the number of complete matches found by SuSe is divided by the number of matches from the baseline. The average of these ratios gives the relative recall improvement.
- **Absolute recall (higher is better):** At each evaluation point, we calculate the ratio of matches found by SuSe to the ground truth (obtained by setting the summary size to the full stream size, capped at 2000).
- **Detected matches recall (higher is better):** The ratio of complete matches that were present in SuSe to all potential matches over time.
- **Execution time (lower is better):** Average time (in seconds) required to process the input stream.
- **Throughput (higher is better):** Average number of processed elements per second.
- **Latency (lower is better):** Average time (in seconds) required to process an element.
- **Memory usage (lower is better):** Maximum memory usage for a run.
  
#### Experiments: 
#### Effectiveness
| Figure | Experiment                               | Description                                                                                                                                   |
| :----: | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
|   6a   | Changing summary / time window sizes     | Evaluate **relative recall improvement (RRI)** as a function of summary size and time window size on synthetic streams.                       |
|   6b   | Changing probability distribution        | **RRI** under different alphabet distributions, while varying summary and time window sizes.                                                  |
|   7a   | Ablation study                           | Compare selection function **present+expected benefit** vs **present‑only**; measure **RRI** to quantify the quality of the expected‑benefit. |

#### Effectiveness (Recall)
| Figure | Experiment                  | Description                                                                                                                    |
| :----: | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
|   7b   | Absolute recall             | **Absolute recall** via ground truth (obtained with summary size = full stream size, capped at 2000) on synthetic streams.     |
|   7c   | Detected matches recall     | Ratio of complete matches present in SuSe over all potential matches over time.                                                |

#### Sensitivity analysis
| Figure | Experiment                                | Description                                                                                                                 |
| :----: | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
|   8a   | # of evaluation timestamps                | Impact of evaluation frequency on **RRI**; <br>**fixed:** summary=500, window=100.                                          |
|   8b   | Pattern length                            | Impact of query length on **RRI**; <br>**fixed:** summary=500, window=100.                                                  |
|   8c   | # of Kleene star operators                | Impact of increasing the number of Kleene stars in a fixed‑size pattern on **RRI**; <br>**fixed:** summary=500, window=100. |
|   8d   | Kleene star position                      | Positional effect of the Kleene operator on **RRI**; <br>**fixed:** summary=500, window=100.                                |
|   8e   | # of disjunction operators                | Impact of increasing disjunctions on **RRI**; <br>**fixed:** summary=500, window=100.                                       |
|   8f   | Overlapping characters (via disjunctions) | Impact of increasing pattern overlap on **RRI**; <br>**fixed:** summary=500, window=100.                                    |

#### Efficiency
| Figure | Experiment                                          | Description                                                                                                           |
| :----: | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
|   9a   | StateSummary vs FlinkCEP / CORE / REmatch - time    | **Execution times** for increasing input lengths using pattern `ABCD`; compares to FlinkCEP, CORE (CEP), and REmatch. |
|   9b   | StateSummary vs FlinkCEP / CORE / REmatch - speedup | **Throughput gain** over baselines for increasing input lengths using pattern `ABCD`.                                 |
|  10a   | Runtime vs summary / time window size               | **Execution time** for processing **100,000** elements while varying summary and time window sizes.                   |
|  10b   | Throughput vs summary / time window size            | **Throughput** for **100,000** elements while varying summary and time window sizes.                                  |
|  10c   | Latency vs summary / time window size               | **Latency** per element for **100,000** elements while varying summary and time window sizes.                         |
|  10d   | Memory experiment                                   | **Maximum memory usage** across summary and time window sizes.                                                        |

#### Real‑world experiments
| Figure | Experiment             | Description                                                                                                     |
| :----: | ---------------------- | --------------------------------------------------------------------------------------------------------------- |
|  11a   | Citi Bike - RRI        | Impact of Citi Bike real-world dataset (~3.8M events) on **RRI** for two queries and summary/time window sizes. |
|  11b   | Citi Bike - throughput | **Throughput** for summary/time window sizes on Citi Bike.                                                      |
|  11c   | Citi Bike - latency    | **Latency** for summary/time window sizes on Citi Bike.                                                         |
|  12a   | NASDAQ - RRI           | Impact of NASDAQ real-world dataset (~462k events) on **RRI** for two queries and summary/time window sizes.    |
|  12b   | NASDAQ - throughput    | **Throughput** for summary/time window sizes on NASDAQ.                                                         |
|  12c   | NASDAQ - latency       | **Latency** for summary/time window sizes on NASDAQ.                                                            |

#### Notes on datasets
- The repository includes scripts and configuration to reproduce both **synthetic** experiments and two **real‑world** case studies (Citi Bike and NASDAQ). For descriptions of character types and queries, we refer to the paper.
- Real‑world datasets summarized in the paper: Citi Bike (~3.8M events for one month) and NASDAQ minute‑level trades (~462K events).

## 9. Troubleshooting

- **No plots but CSVs are present.** Re-run quickstart command to trigger plot post‑processing.
- **Paper PDF wasn’t produced.** Ensure the `paper/` directory and `summarySelector_sigmod25_cameraReady.tex` are present; inspect `./runs/_logs/paper__pdflatex__*.log`.
- **I want to re-run only plotting.** Remove figure PDFs under the experiment directory and run the quickstart command again.
- **Docker.** You must be able to run `docker` (via `sudo` or by being in the `docker` group ([see here](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user))).
- **Execution rights.** If a script fails with ,,Permission denied'', restore execute bits from the `./reproducibility_submission/` directory via:
```bash
find . -type f \
  \( -name '*.sh' -o -name 'summary_selector' -o -name 'rematch' \
     -o \( -path '*/FLINK/flink_cep/deploying/*' -not -name '*.*' \) \
  \) -exec chmod +x {} +
```
  and re-run the experiment.
  - **Citi Bike dataset download failed.** Check internet connectivity and, as a fallback, pre‑seed the data directory:
  1) Manually download the Citi Bike trip data CSV file: https://box.hu-berlin.de/f/b791c68aedcc4b578e29/
  2) Place it in `real_world_experiments/citi_bike/query0/` and `real_world_experiments/citi_bike/query1/`.
  3) Re-run `./run_repro.sh`.

---

**Short reference**

- One‑shot: `./run_repro.sh`
- Orchestrator: `python3 run_all.py [--force] [--keep-going] [--dry-run] [--extensive-reproducibility]`
- Artifacts: `./runs/…`
- Logs: `./runs/_logs/…`

