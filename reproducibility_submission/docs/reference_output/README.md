## Comments on figure differences (small sample sizes)

The reproduced plots closely match the original plots. Below we note minor differences, explain their causes, and detail the significant discrepancy in Fig. 11 caused by a bug.

### Figure 7a - Ablation study

The overall trend matches the original paper. Differences at time‑window size 250 stem from the reduced sample sizes used for reproduction (see §3.1). Running with paper‑scale sampling (`--extensive-reproducibility`) restores the original `NUM_OF_RUNS` but adds ~24 hours.

---

### Figures 9a,b - FlinkCEP, CORE, REmatch efficiency

We reduced the maximum tested word length for REmatch and CORE from 4096 to 2048. The two dropped data points would add ~2 days of runtime; the trend is already clear with the remaining lengths. The `evaluation*.sh` scripts for CORE and REmatch still include commented lines to re‑enable length 4096 if needed.

---

### Figure 10d - Memory experiment

The plot looks different mainly due to the y‑axis scale. Although the reproduced system used up to ~40 MB more memory, there are no trends visible across different parameter combinations, consistent with the original paper.

---

### Figure 11a - Why our reproduction differs

In the paper, Fig. 11a was the only case where baselines outperformed SuSe for some parameter settings. In reproduction, we could not replicate the results of Fig. 11a and observed non‑determinism despite fixed seeds.

**Root cause (Citi Bike script race):** We launched many runs in parallel. An outdated `run_test.sh` reused a shared probabilities file:

```bash
if [ -f ${PROB_FILENAME} ]; then
  echo "...already exists, reusing"
else
  echo "...does not exist yet, creating"
  python3 citibike_event_stream_generator.py \
    --file_name="${FILE_NAME}" \
    --produce_alphabet_probs \
  > ${PROB_FILENAME}
fi
```

Parallel runs sometimes read the file **before it was written** (empty file). Our code interprets an empty probabilities file as ,,all character probabilities are zero'', which forces the **expected benefit to be always 0**. The selection strategy then collapses to **present benefit only** (as also seen in the ablation), making (bad) local optima likely.

**Fix (unique temp file per run):**
```bash
PROB_FILENAME=$(mktemp)
echo "Storing probabilities in: ${PROB_FILENAME}"

python3 citibike_event_stream_generator.py \
    --file_name="${FILE_NAME}" \
    --produce_alphabet_probs \
> ${PROB_FILENAME}

```

Each run now gets its own correct probabilities file and fully leverages the expected benefit. The results are now deterministic, improved significantly and align with the rest of the paper, especially the NASDAQ experiment (Fig. 12a).

---

### Figure 11b - Extra throughput data points

The additional points in the *original* throughput plot came from earlier Citi Bike runs for queries `Q0` and `Q1`.

- We tested all combinations: summary sizes `{100, 250, 500}` x time‑window sizes `{100, 250, 500}`.
- **Produced results:** `Q0` -> `{250, 500}`; `Q1` -> `{500}` only.
- Combinations that **produced no results** were excluded from recall/RRI plots but **still contributed to the throughput plot**, and we forgot to remove them from Fig. 11b.
- For reproducibility, we re‑ran only the combinations that previously produced results (to reduce time), so there are fewer throughput data points. The overlapping points are consistent with the original figure, though.
