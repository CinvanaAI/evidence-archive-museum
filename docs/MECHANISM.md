# Evidence Archive Museum: mechanism

[load_archive](../evidence_archive_museum/archive.py) validates identities, source labels and references among records/groups/eras/dispositions. [render_html](../evidence_archive_museum/render.py) embeds the validated data safely into a portable reader and writes the final page atomically. See [DATA_FORMAT.md](../DATA_FORMAT.md) for the input schema. The output needs no server or database.

The CLI loads and validates before rendering. `render_html` serializes only the normalized archive, escapes characters that could break out of its JSON script element, and uses DOM text content for record prose. `write_html` writes and flushes a temporary file beside the destination before replacing the destination. The CLI requires `--force` for an existing file; direct callers of `write_html` are responsible for their overwrite policy.

The reader holds no separate database: topic-to-record navigation selects the exact IDs in `record_ids` from the embedded data. A record search is applied within that selection until **Show all records** or the Records navigation button clears it. The four input files remain the source of truth; editing the HTML does not update them. See the [worked example](WORKED-EXAMPLE.md) for one record's complete path.

## Limits that matter

Validation establishes internal structure, not truth of the records. Source-path fields are labels rather than links that the tool fetches. Treat archive inputs as the deliberate public selection: the renderer cannot decide which source material you are authorized to share.

## Demonstration contract

Input: Four synthetic archive records with group, era and disposition data.

Expected observation: A validated self-contained searchable HTML exhibit.

The bundled example uses synthetic material. Its observed output establishes that bounded path, not every possible integration.
