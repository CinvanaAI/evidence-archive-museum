# Evidence Archive Museum

Turn a folder of structured records into an exhibit someone can explore: start with a topic, open the records behind it, and follow its dates and relationships.

The idea came from a practical archive problem: a polished story can lose its connection to the material it describes. Here the page is generated from explicit records, memberships and source references. Change the data and rebuild the view. The [public extraction](ORIGIN.md) replaces the original private archive with a small JSON contract and invented examples.

**A portable offline generator.** Python builds one HTML file; the reader needs a browser and no account, service or database. [Walk through the example](docs/WORKED-EXAMPLE.md) · [Prepare your own archive](DATA_FORMAT.md)

![Synthetic demonstration](docs/images/museum-desktop.png)

## Try it

Python 3.11 or newer.

```sh
python -m pip install -e .
python -m evidence_archive_museum.cli validate examples/synthetic_archive
python -m evidence_archive_museum.cli build examples/synthetic_archive --output demo-museum.html
```

Open `demo-museum.html` locally, or download and open the included [example exhibit](example-site/index.html). The [synthetic archive](examples/synthetic_archive/records.jsonl) has four records, three groups, two eras and four source references. Choose **Read 2 records** on the Museum topic: you should see “Offline museum generated” and “Lineage made explicit.” Search within that group, then choose **Show all records** to return to the full set.

These four events and their source labels are invented demonstration data, not a history of this project's development. The [worked example](docs/WORKED-EXAMPLE.md) traces the inputs and explains every counter. Edit a copy of the input and rebuild to see how its relationships change. Existing output is protected unless `--force` is passed.

## How it works

1. Load records, topic memberships, eras and dispositions from four files.
2. Reject duplicate IDs, missing references, unsupported statuses and invalid date ranges.
3. Recompute counts and embed the accepted data with the reader's code in one HTML file.
4. Search and navigate that embedded data locally. No source files are opened by the reader.

[Follow the implementation](docs/MECHANISM.md). Topic adjacency means a declared relationship; succession is separately recorded in dispositions. Neither is inferred from a title or a narrative.

## Scope

Validation establishes internal structure, not truth of the records. Source-path fields are labels rather than links that the tool fetches. Treat archive inputs as the deliberate public selection: the renderer cannot decide which source material you are authorized to share.

Use it for a selected project chronicle, experiment collection or small evidence catalogue. A private research vault requiring access controls, attached documents or automatic updates needs additional machinery. The input limits are 10,000 records, 1,000 groups and 200 eras, with file-size caps; these are validation limits, not a performance claim at those sizes.

## Possible next steps

Useful extensions could include an explicit reviewed attachment bundle and saved links to an individual record. These are current possibilities, not implemented features or a release promise. Keeping the exhibit portable and making source access deliberate are the design constraints for either.

## Verify

`python -m pytest` runs the behavior tests (install `pytest` first). The runnable example above provides a separate first-use check.

MIT licensed; see [LICENSE.md](LICENSE.md). Origin and release boundaries are documented in [ORIGIN.md](ORIGIN.md) and [SECURITY.md](SECURITY.md).
## Inspect the example result

Open the [saved synthetic result](example-site/index.html) alongside its [input and demonstration](examples/synthetic_archive/records.jsonl). The result is from the bundled synthetic example; local machine paths and temporary run identifiers are excluded from public projections.
