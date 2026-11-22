---
type: community
cohesion: 0.07
members: 44
---

# Document Extraction Tools

**Cohesion:** 0.07 - loosely connected
**Members:** 44 nodes

## Members
- [[BIFF8 shared-string table, strings may span CONTINUE records.]] - rationale - jarvis-pro/agent/data.py
- [[Collapse spaces, keep line breaks, drop control chars.]] - rationale - jarvis-pro/agent/data.py
- [[Excel 97-2003 (BIFF8) shared strings + textnumber cells, one line per row.]] - rationale - jarvis-pro/agent/data.py
- [[Fallback when the file is not a readable OLE2 WordExcel UTF-16 runs of…]] - rationale - jarvis-pro/agent/data.py
- [[Rows as 'a  b  c' lines, shared strings substituted (prices stay next to…]] - rationale - jarvis-pro/agent/data.py
- [[Streams of an OLE2 compound file as {name bytes}. Stdlib-only, bounded loops.]] - rationale - jarvis-pro/agent/data.py
- [[THE ONLY FILE THAT TOUCHES REAL DATA. JARVIS_DEMO=1 (default) - invented…]] - rationale - jarvis-pro/agent/data.py
- [[Word 97-2003 read the piece table, so Vietnamese text comes out whole.]] - rationale - jarvis-pro/agent/data.py
- [[Yield (source_root, relative_path, text). Read-only.]] - rationale - jarvis-pro/agent/data.py
- [[_cfb()]] - code - jarvis-pro/agent/data.py
- [[_clean()]] - code - jarvis-pro/agent/data.py
- [[_doc()]] - code - jarvis-pro/agent/data.py
- [[_docx()]] - code - jarvis-pro/agent/data.py
- [[_f()]] - code - jarvis-pro/agent/data.py
- [[_local()]] - code - jarvis-pro/agent/data.py
- [[_num()]] - code - jarvis-pro/agent/data.py
- [[_ole_text()]] - code - jarvis-pro/agent/data.py
- [[_pdf()]] - code - jarvis-pro/agent/data.py
- [[_pdf_ops()]] - code - jarvis-pro/agent/data.py
- [[_rk()]] - code - jarvis-pro/agent/data.py
- [[_sst()]] - code - jarvis-pro/agent/data.py
- [[_u16hex()]] - code - jarvis-pro/agent/data.py
- [[_xls()]] - code - jarvis-pro/agent/data.py
- [[_xlsx()]] - code - jarvis-pro/agent/data.py
- [[agentdata.py]] - code - jarvis-pro/agent/data.py
- [[body()]] - code - jarvis-pro/agent/data.py
- [[chain()]] - code - jarvis-pro/agent/data.py
- [[cmap()]] - code - jarvis-pro/agent/data.py
- [[concurrent_futures]] - concept
- [[dec()]] - code - jarvis-pro/agent/data.py
- [[email]] - concept
- [[email_utils]] - concept
- [[extract()]] - code - jarvis-pro/agent/data.py
- [[fonts_in()]] - code - jarvis-pro/agent/data.py
- [[google_reset()]] - code - jarvis-pro/agent/data.py
- [[inbox_dir()]] - code - jarvis-pro/agent/data.py
- [[iter_documents()]] - code - jarvis-pro/agent/data.py
- [[need()]] - code - jarvis-pro/agent/data.py
- [[put()]] - code - jarvis-pro/agent/data.py
- [[sources()]] - code - jarvis-pro/agent/data.py
- [[struct]] - concept
- [[take()]] - code - jarvis-pro/agent/data.py
- [[xml_etree_elementtree]] - concept
- [[zlib]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Document_Extraction_Tools
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Agent Tooling Framework]]
- 6 edges to [[_COMMUNITY_re]]
- 4 edges to [[_COMMUNITY_Data Parsing Utilities]]
- 4 edges to [[_COMMUNITY__gmail_body]]
- 2 edges to [[_COMMUNITY_google_source]]
- 2 edges to [[_COMMUNITY_Product Profile Generator]]
- 2 edges to [[_COMMUNITY_google_auth.py]]
- 2 edges to [[_COMMUNITY_TAI-LIEU-KINH-DOANHbuild.py]]
- 1 edge to [[_COMMUNITY_Document Processing Utilities]]

## Top bridge nodes
- [[agentdata.py]] - degree 55, connects to 9 communities
- [[extract()]] - degree 8, connects to 1 community
- [[iter_documents()]] - degree 5, connects to 1 community
- [[inbox_dir()]] - degree 2, connects to 1 community