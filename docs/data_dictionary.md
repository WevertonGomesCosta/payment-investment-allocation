# Data Dictionary

## Input sheets

### `Todos os Gastos`
Expected logical fields:

- date
- description
- value
- paid flag
- primary lot used
- secondary lot used

### `Inventário de Lotes`
Expected logical fields:

- lot id
- entry date
- original value
- investment/product reference

### `Carteira`
Expected logical fields:

- product name
- product type
- indexer
- base rate
- bonus rate
- bonus days
- term days
- lockup days
- tax exemption flag
- min/max application
- active flag
- combo flags and ratios

## Internal normalized entities

- normalized expenses
- normalized lots
- normalized portfolio products
- historical lot-event links
- initialized prospective state
