# semaglutide-tte

Results and plotting scripts for the semaglutide target trial emulation (TTE) study on Danish hospital EHR data.

Effect estimates were obtained with the causal pipeline in [PHAIR_EHR](https://github.com/kirilklein/PHAIR_EHR) (transformer-based propensity and outcome models on MEDS-formatted EHR) and [CausalEstimate](https://github.com/kirilklein/CausalEstimate) (IPW / TMLE estimators).

## Contents

- `results/estimates/<version>/causal_results.csv` — effect estimates per method (`IPW`, `TMLE`, plus unadjusted `RD`/`RR`) and outcome, with standard errors and 95% CIs
- `figures/estimates/<version>/` — forest plots generated from the results
- `code/plotting/` — scripts to reproduce the figures:
  - `estimates.py` — forest plot of effect estimates with 95% CI
  - `confounders.py` — covariate balance
  - `overview_risk.py` — risk overview per group

## Outcomes

All-cause death, death/MI/stroke composite, hospitalization with heart failure, nonfatal MI, nonfatal stroke.

## Reproduce figures

```bash
python code/plotting/estimates.py results/estimates/v01/causal_results.csv
```

## Citation

Paper reference to be added.

## License

MIT
