# Controlled writer transfer

This is a checklist, not executable production automation. Test recovery on a
disposable environment and adapt it to your PostgreSQL distribution and services.

1. Inventory every writer, scheduled job, notification sender and privileged
   maintenance process. Verify exact release, database system identity, compatible
   PostgreSQL versions, checksums, disk space, TLS and clock alignment.
2. Stop all application writers and persist their restart holds. Block ordinary
   database connections. Ensure no prepared transactions, unlogged application
   tables or unexpected databases are being left out of the plan.
3. Record a quiescent WAL barrier, table counts and aggregate hashes, schema hash
   and safe sequence high-water marks. Do not export user records into receipts.
4. Verify the standby replayed the barrier and matches the dataset. Physical
   standby sequence values may be safely ahead due to WAL prelogging; they must
   not move behind the source or reuse IDs.
5. Cleanly stop and persistently fence the former writer. Verify local process,
   listener, supervisor and actual PostgreSQL shutdown state. An unreachable peer
   is insufficient evidence. Keep evidence bound to this operation and short-lived.
6. Promote once. If the command times out, inspect actual state before continuing.
7. Rejoin the former writer as a standby, using a fresh working seed or reviewed
   `pg_rewind`. Preserve the former data until recovery has been verified. A partial
   rewind can invalidate its target; it is not an automatic rollback.
8. Change API database locality, write/read-only roles, background job ownership,
   routing, monitor expectations, DNS ownership and release tooling together.
9. Check replication, role enforcement, sessions, privacy, HTTPS, asset hashes and
   safe-read fallback before reopening writes. Record actual timings after transfer.

Before promotion, restore the old writer only while the target is still a standby.
After promotion, the old writer must never restart as a writer. An application
binary rollback does not reverse database ownership; a reverse transfer needs its
own fenced procedure.

## Pilot validation

The pilot transfer compared the application schema, table hashes and sequence
high-water marks before promotion and after the former writer rejoined. Its
fresh working replica passed `pg_verifybackup`. The retired transfer directory
was removed only after streamed recovery, API role checks and release verification.

A bounded process-loss drill stopped only the app API, not a host or database.
Both HTTPS entry points continued safe reads, rejected mutations with a read-only
service response, and returned to the writer after restart. This establishes the
tested API fallback path. It does not establish full-host DNS recovery or prove
lossless automatic database promotion.

An operator launcher timeout once left a still-running seed child. Inspect the
actual process and progress before retrying; a timeout is not proof that the
underlying copy stopped. Verify a completed manifest before finalizing it, and
do not run a second seed into the same directory.

## Recovery drills

First test local API-process loss. Separately test reserve GET behavior, denied
writes, private-link loss and incompatible-release rejection. Full host failure
and database promotion drills need their own recovery plan. Mocked policy tests
are useful, but do not prove a real machine was fenced.

An uncertain failed mutation must not be blindly replayed on another server.
Use idempotency keys for retryable writes, and keep Nginx's `non_idempotent` retry
option disabled. Session refresh has its own explicitly audited contract.

## References

- [PostgreSQL failover](https://www.postgresql.org/docs/18/warm-standby-failover.html)
- [PostgreSQL pg_rewind](https://www.postgresql.org/docs/18/app-pgrewind.html)
- [PostgreSQL pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html)
- [Nginx upstream retry](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream)
