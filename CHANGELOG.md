# Changelog

## 0.2.0 - Official baseline consolidation

- Consolidated **v2** as the official baseline for continued development
- Archived **v5** as an experimental methodological branch
- Added baseline governance documentation
- Opened the next development stage explicitly on top of v2

## 0.1.1 - Hardened intertemporal joint policy

- Switching decisions now re-evaluate the remaining horizon instead of only the local critical day
- Joint policy defaults to the strongest switching candidate per critical date to keep the replay tractable

## 0.1.0 - Initial methodological phase

- Minimal configuration loader
- Workbook loading
- Data normalization
- Historical reconstruction
- Initial pricing engine
- Future payment diagnosis
- Local redemption candidate engine
- Intertemporal redemption policy
- Canonical switching contracts and invariants
- Switching candidate generation on critical dates
- Compare switching candidates against current intertemporal redemption selections on critical dates
- Switching-aware intertemporal policy with same-day switching-before-redemption evaluation

## 0.2.1 - Baseline guardrails on top of v2
- Added official v2 baseline reference file
- Added baseline guardrails module
- Added validation script for future refinements
- Documented required acceptance checks for the official line

## 0.2.1 - Bonus-dominance switching block
- Added switching restriction for origins with dominant remaining bonus period
- Switching contracts now reject destinations when the origin still dominates over the comparable bonus window
- Added inspection tooling for remaining-bonus switching eligibility

- Replaced fixed lot-level switching blocks with a programmatic structural-dominance rule on the origin portfolio.

## 0.2.3 - Full end-to-end baseline confirmation
- Optimized the full joint-policy replay enough to re-run it end-to-end with the programmatic origin-dominance rule enabled
- Added a confirmation script comparing the full resulting trajectory against the official v2 baseline
- Stored the official v2 switching trajectory for reproducible confirmation


## 0.2.1 - Operational workbook export
- Added `exportacao_workbook_operacional_principal.py`
- Added `gerar_workbook_operacional_principal_v2.py`
- Added operational workbook generation aligned with the reference workbook
- Simplified workbook structure for practical validation


## 0.2.2 - Workbook and console readability improvements
- Split received lots into `Recebidos_Ativos` and `Recebidos_Historico`
- Renamed switching views to `Switchings_Por_Evento` and `Switchings_Agrupados`
- Adopted Brasília current date (`America/Sao_Paulo`) as reference date for day counts
- Added detailed console summary with active/historical lots and switching sections
