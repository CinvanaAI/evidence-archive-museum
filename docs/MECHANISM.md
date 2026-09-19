# Evidence Archive Museum: mechanism

[load_archive](../evidence_archive_museum/archive.py) validates identities, source labels and references among records/groups/eras/dispositions. [render_html](../evidence_archive_museum/render.py) embeds the validated data safely into a portable reader and writes the final page atomically. See [DATA_FORMAT.md](../DATA_FORMAT.md) for the input schema. The output needs no server or database.

## Limits that matter

Validation establishes internal structure, not truth of the records. Source-path fields are labels rather than links that the tool fetches. Treat archive inputs as the deliberate public selection: the renderer cannot decide which source material you are authorized to share.

## Demonstration contract

Input: Four synthetic archive records with group, era and disposition data.

Expected observation: A validated self-contained searchable HTML exhibit.

The bundled example uses synthetic material. Its observed output establishes that bounded path, not every possible integration.
