# Data (not included)
Raw data cannot be redistributed. To run `myanmar_conflict_analysis.py`, download each dataset
from its provider (check their terms of use) and place the files next to the script:

| Dataset | Provider | Needed columns |
|---|---|---|
| Township boundaries (shapefile) | Myanmar Information Management Unit (MIMU) | `TS_PCODE` |
| Conflict fatalities per township | ACLED (free registration), summed per township | `TS_PCODE`, `fatal_post` |
| Population per township | 2014 Myanmar Census | `TS_PCODE`, `Total_Population` |

All three tables must be at **township** level and share the same `TS_PCODE` values. The script stops with
an error if populations are missing or fatalities exceed population.
