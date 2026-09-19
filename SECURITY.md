# Security and Privacy

- The renderer is offline and produces a single dependency-free HTML file.
- Archive files have count and byte-size limits.
- Source paths must be relative POSIX paths; absolute machine paths and parent traversal are rejected.
- Embedded archive JSON escapes characters that could terminate the data script, and the client renderer places archive values through `textContent` rather than HTML interpretation.
- The output file is written atomically and is not replaced without `--force`.
- No source evidence is opened, copied, fetched, or embedded by the renderer.

The generated page is still a complete readable copy of the archive metadata. Do not build it from private records and then publish the HTML without a separate content review.
