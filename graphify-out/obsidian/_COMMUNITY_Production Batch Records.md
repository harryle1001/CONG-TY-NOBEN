---
type: community
cohesion: 1.00
members: 3
---

# Production Batch Records

**Cohesion:** 1.00 - tightly connected
**Members:** 3 nodes

## Members
- [[graphify-setup.sh]] - code - tools/graphify-setup.sh
- [[graphify-setup.sh script]] - code - tools/graphify-setup.sh
- [[say()]] - code - tools/graphify-setup.sh

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Production_Batch_Records
SORT file.name ASC
```
