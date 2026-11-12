# Earth Engine apps

Six scripts for the Google Earth Engine code editor. They show the Magdalena basin, a water-body layer coloured by the sentiment of the news of the chosen year, and an inspector that opens on click.

| Script | Water-body layer (asset) | Extra layer |
|---|---|---|
| `Rios.js` | `RiosMagdalena` | none |
| `Cienagas.js` | `CienagasMagdalena` | none |
| `Lagunas.js` | `LagunasMagdalena` | none |
| `Embalses.js` | `EmbalsesMagdalena` | none |
| `Precipitacion.js` | `RiosMagdalena` | ERA5 monthly total precipitation |
| `Temperatura.js` | `RiosMagdalena` | ERA5 monthly 2 m air temperature |

Assets live under `users/santiagoduarte09/lasantamaria/` (plus `areamagda` for the basin outline). To run the scripts under another account, upload the shapefiles, share them, and change those paths.

## Property names the scripts read

For each year `YYYY` (2016-2020) the feature table needs `Element`, `Class` and

| Property | Content | Produced by |
|---|---|---|
| `Sent YYYY` | mean sentiment as text, or `Not Info` | `santamaria.aggregate.to_gee_table` |
| `Top YYYY` | key words | same |
| `Art YYYY` | number of articles | same |
| `Tens YYYY` | `Malo`, `Neutro`, `Bueno` or `No` | same |

Public app: https://santiagoduarte09.users.earthengine.app/ (from the workflow diagram).
