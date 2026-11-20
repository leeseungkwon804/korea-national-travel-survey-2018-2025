# Korea National Travel Survey, 2018 to 2025: analysis code

Analysis code for two manuscripts using the respondent level microdata of the Korea National
Travel Survey (national approved statistic no. 314001), produced by the Korea Culture and Tourism
Institute.

- **Paper A** Trading Down and Dropping Out in Household Leisure Travel After a Systemic Shock
- **Paper B** Asymmetric Regional Resilience and Negative Coupling Between the Overnight and Day
  Trip Subsystems of a National Tourism System

## Data

The microdata are **not redistributed here**. They are publicly available from the Tourism
Knowledge and Information System at
https://know.tour.go.kr/stat/nRawDataDownloadDis19Re.do subject to completion of the provider's
user registration form. Files are supplied as zip archives containing both XLSX and SPSS formats.
Accessed 19 November 2026.

Eight annual waves are used, 2018 to 2025, totalling **382,024 respondent records**.

## Four comparability issues that the code handles

These were identified by variable level and value label comparison across all eight files and are
documented in `outputs/Table_S1_variable_audit.csv`.

1. **Regime break before 2018.** The producing agency states that the 2018 instrument redesign
   makes 2017 and earlier not comparable with 2018 and later. Earlier waves are excluded.
2. **Trip count variables change definition at the 2020 wave.** In 2018 and 2019 the derived trip
   count variables carry a label qualifier indicating adjustment for trips extending beyond the
   reference month, applied to 759 and 810 variables respectively. From 2020 no variable carries
   it. This is **not documented in the agency user guide**. Trip count measures are therefore not
   comparable across that boundary, and the analyses use participation measures only, whose
   variable labels are identical in all eight waves.
3. **Region code scheme differs by wave.** The 2019 file codes regions administratively, where 11
   denotes Seoul. From 2020 the same variable uses sequential numbering, where 11 denotes North
   Chungcheong. Pooling without recoding silently mislabels regions. The mapping is verified
   against the value labels stored in each file.
4. **Participation variables are coded 0/1 in 2020 to 2024 and 0/100 in 2025.**

## Running order

| Script | Purpose |
|---|---|
| `code/extract_sav.py` | extract the SPSS files from the provider archives |
| `code/meta.py` | read metadata, build the variable inventory |
| `code/final.py` | weighted participation series, all waves |
| `code/agestd.py` | direct age standardisation to the 2019 age structure |
| `code/robust.py`, `code/rob2.py` | robustness analyses |
| `code/paperB.py` | regional subsystem panel and resilience indices |
| `code/ml.py` | classification of the substitution margin, permutation importance |
| `code/tables.py` | manuscript tables |
| `code/figsAB.py`, `code/figML.py`, `code/figregime.py` | figures |

## Environment

Python 3.12.2, pandas 2.2.2, numpy 1.26.4, pyreadstat 1.3.8, scikit-learn 1.8.0, matplotlib 3.10.8.

## Generative AI

Claude (Anthropic), Claude Code version 2.1.325 was used to generate analysis code and to assist
with manuscript drafting. All code was executed and its numerical results verified against the
source files by the author, who takes full responsibility for the content.

## Licence

MIT.
