# Changelog

## 0.1.1 - Switching contracts and invariants

- Canonical switching enums and dataclasses
- Individual switching contract skeleton
- Switching invariant checks for origin, destination, and lineage
- Minimum economic comparison between keep, redeem, and switch
- Switching documentation and architecture update

## 0.1.0 - Initial methodological phase

- Minimal configuration loader
- Workbook loading
- Data normalization
- Historical reconstruction
- Initial pricing engine
- Future payment diagnosis
- Local redemption candidate engine
- Intertemporal redemption policy

- Switching candidate generation on critical dates
- Compare switching candidates against current intertemporal redemption selections on critical dates

- switching-aware intertemporal policy with same-day switching-before-redemption evaluation


## 0.1.1 - Hardened intertemporal joint policy
- Switching decisions now re-evaluate the remaining horizon instead of only the local critical day
- Joint policy defaults to the strongest switching candidate per critical date to keep the replay tractable

- top_k_switch_por_data sensitivity support for intertemporal switching policy


## 0.1.1 - Hardened global switching policy
- Added materiality filtering for switching decisions
- Added size variants for candidate switching evaluation
- Added dominant-lot future reserve preservation
- Hardened horizon-wide switching policy evaluation
