# Measure the cause before changing topology

Compare the same authenticated route, account, encoding, data shape and release.
Keep tokens and content in memory; export timings, byte counts and aggregate
counts only. Separate cold connection time from warm query roundtrips.

Record local API time, public time to first byte, total time, decoded response
size, compressed bytes, database RTT, CPU, available memory, disk pressure,
network throughput, error rate and worker identity. A fast health endpoint alone
does not measure a social feed or a write.

## Case-study observations

Small pre-transfer samples showed local SQL roundtrips near 0.3 ms and remote
ones near 35–45 ms. A compact goal overview was about 4.6 KB compressed, while
an API using the remote database took roughly 239–662 ms. The uplink was mostly
idle. These samples identify latency, not a maximum concurrent-user capacity.

We also found a like/comment join multiplying rows before grouping. On a fixed
synthetic PostgreSQL 18 fixture (120 reports, 40 likes and 40 comments per report,
page size 24), separate indexed counts reduced the largest intermediate result
from 192,000 rows to 120. One run measured 154 ms versus 2.6 ms. This is a query
benchmark, not a promise that all screens became 59 times faster.

Repeated inline avatar strings can inflate decoded JSON even when compression
reduces wire bytes. A response-local shared avatar map avoids repeated strings
without creating a cross-user photo cache. Legacy clients retain their DTO shape;
new clients restore ordinary DTOs before rendering or persistence.

After the transfer, two bounded read-only samples of the 24-item shared-avatar
feed returned about 100–155 ms at the app origin. The compact overview returned
about 183–224 ms. Warm local SQL probes usually took 0.3–1.7 ms; first connection
setup was measured separately. This removes the cross-server database dependency
but is not a high-concurrency load test.

Decoded feed JSON fell from roughly 1.48 MB to 106 KB for the same data. Compressed
transfer remained near 63 KB because compression already removed much repeated
text. The gain is less JSON allocation and parsing, not a fourteenfold reduction
in network traffic.

## Client behavior

Cache personalized data per account, deduplicate concurrent reads, preserve the
original disk snapshot timestamp, invalidate after mutations, reject late reads
after account switches and clear content after authoritative permission denial.
Keep loaded content during background refresh, including an already-loaded empty
list. Initial skeletons should match content geometry, support reduced motion and
announce a local status without stealing focus or inventing percentages.

Do not put private API responses into a shared Nginx/CDN cache. Hash-named static
assets can use long immutable caching; HTML needs revalidation so updates remain
discoverable. Pagination must preserve calendar/history contracts rather than
silently discarding old progress.

## Next measurements

Use bounded synthetic load outside production first. Report p50/p95/p99, errors,
database connections and RSS with the dataset and concurrency stated. Pool sizes
are a system-wide budget; raising every worker's limit is not a free speedup.

- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)
- [PostgreSQL multicolumn indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [node-postgres pool sizing](https://node-postgres.com/guides/pool-sizing)
- [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
