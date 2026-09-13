The canary runs the **same** `app.py` as `services/stable` — byte for byte. It is duplicated here
(rather than symlinked or shared) only so each service has a self-contained Docker build context.

Every behavioural difference between stable and canary comes from environment variables set in
`docker-compose.yml` and overwritten by `scenarios/*.sh` (CLAUDE.md §5.1). If you edit one app.py,
copy it to the other; `tests/test_e2e.py` should assert the two files are identical.
