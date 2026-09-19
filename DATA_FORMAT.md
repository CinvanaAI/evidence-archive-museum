# Data Format

An archive directory contains four files.

## `records.jsonl`

One JSON object per line:

```json
{"id":"record-001","title":"A finding","summary":"What the evidence supports.","date":"2025-03-12","sources":["evidence/run.json"],"tags":["provenance"]}
```

Every record requires at least one relative POSIX source path. Absolute paths, drive letters, backslashes, and parent traversal are rejected.

## `groups.json`

An array of topic objects with `id`, `title`, `narrative`, `record_ids`, and `adjacent`. Every referenced record and adjacent group must exist; self-adjacency is rejected.

## `eras.json`

An array with `id`, `title`, `summary`, ISO `start`, ISO `end`, and `group_ids`. Dates must be ordered and every group must exist.

## `dispositions.json`

An object keyed by group ID. Each value has `status`, optional `successor`, and optional `notes`. Supported statuses are `active`, `superseded`, `record`, `idea`, and `deferred`.

The example archive is the executable specification.
