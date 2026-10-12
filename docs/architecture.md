# Architecture and boundaries

The application VPS owns one writable PostgreSQL cluster and the application API.
Its normal requests never cross the private link for SQL. The services VPS owns
mail, the landing website and independent products. Its application database is
a physical hot standby, accessed by a read-only API only during recovery.

Keep these concerns independent:

1. **HTTPS entry:** both nodes need valid certificates and matching static assets.
2. **Application role:** one normal API, one explicitly read-only reserve API.
3. **Database role:** one writer, one asynchronous physical standby.
4. **DNS recovery:** a narrowly scoped controller outside the node it recovers.
5. **Promotion:** a separate fenced operator procedure, never a DNS side effect.

A stale DNS cache may still send a visitor to the services node. Its application
edge forwards to the application API over the private link while that API is
healthy. It may serve local reserve reads on a failure. Other product hostnames
continue to route to their own services, rather than through that application.

Use authenticated private connectivity and pinned database TLS. Listen for
PostgreSQL only on localhost and the private interface, restrict the peer address,
use SCRAM and a replication-only account, and monitor certificate expiry.
Public port exposure is not required for replication.

For asynchronous streaming, distinguish application availability from freshness.
A standby can be reachable yet behind. Reserve health should report replay lag,
recovery state, schema/release compatibility and read-only enforcement. DNS must
not redirect traffic to an incompatible or excessively stale reserve.

DNS-only hosting avoids an HTTP proxy dependency. It does not promise connectivity
from every country or ISP. TTL is a cache lifetime, not a guaranteed failover time.
Controllers must own disjoint records and have scoped, expiring credentials.

## Storage

Unique workloads can use both disks. The application database, necessary uploads
and current frontend must be copied if they are expected to survive a host loss.
Asynchronous replication needs room for WAL; replication slots need retention
limits and monitoring. Abandoned slots can consume disk. Retired working data
must have an explicit post-verification retention decision.

## Growth

Measure first. Increase a single app node's resources before introducing remote
SQL roundtrips into normal requests. Then consider object storage for media,
bounded cursor pagination, background jobs and independently scaled stateless
workers close to the writer. Cross-worker personalized caching requires explicit
invalidation. An external witness/fencing mechanism is a separate availability
project, not something achieved by adding round-robin DNS.
