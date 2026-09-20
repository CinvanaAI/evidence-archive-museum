# From one record to an explorable archive

This example is completely synthetic. The event dates, story and source paths illustrate the format; no original private records or evidence files are included.

## Follow the Museum topic

In [records.jsonl](../examples/synthetic_archive/records.jsonl), `record-003` is “Offline museum generated.” It has a date, a summary, tags and the label `evidence/museum/build-summary.json`. That label tells a reader what evidence the author refers to. It is not a file the tool has found or verified.

In [groups.json](../examples/synthetic_archive/groups.json), the `museum` group explicitly lists `record-003` and `record-004`. The reader's **Read 2 records** button selects exactly those IDs. Searching `lineage` within that view leaves only “Lineage made explicit.” **Show all records** clears both the group selection and the search.

In [eras.json](../examples/synthetic_archive/eras.json), `publication` lists the `museum` group for its July–December 2025 range. An era is authored grouping data; the loader checks ordered dates and valid group references. It does not automatically derive era membership from record dates or verify that every record lies within that interval.

In [dispositions.json](../examples/synthetic_archive/dispositions.json), `museum` is active, while `importer` is superseded by `validator`. A successor is a separate claim from adjacency. The four directed adjacency references are importer → validator, validator → importer, validator → museum, and museum → validator.

## Reproduce the build

From a checkout, after installing with `python -m pip install -e .`:

```sh
python -m evidence_archive_museum.cli validate examples/synthetic_archive
python -m evidence_archive_museum.cli build examples/synthetic_archive --output demo-museum.html --title "Synthetic archive — Evidence Archive Museum"
```

The validation prints:

```json
{
  "records": 4,
  "records_with_sources": 4,
  "source_references": 4,
  "groups": 3,
  "eras": 2,
  "adjacency_links": 4,
  "dispositions": 3
}
```

`records_with_sources` counts records containing at least one source label. `source_references` counts the labels, including repeats if supplied. `adjacency_links` counts the directed entries above; it is not the number of unique undirected pairs. None measures whether the evidence supports the author's claim.

Open the HTML file in your browser. Overview shows these counts and topic cards; Timeline shows the two authored eras; Projects lets you search topics; Records lets you search the full set or a selected topic's members. The page contains its own script, style and data and needs no server. JavaScript is required for the interactive reader.

## Make a safe change

Copy the four example input files to a new directory. Change `record-003`'s title, validate that copied directory, and build to a new output filename. The record's topic membership stays intact because the group references its stable ID, not its title. Changing the ID without updating the group instead fails validation with a missing-record reference.

Building to an existing output without `--force` fails and keeps the old file. Use a new filename when comparing editions. The inputs are read; the build writes only the requested output and its temporary file. Archive review and privacy selection happen before generation.
