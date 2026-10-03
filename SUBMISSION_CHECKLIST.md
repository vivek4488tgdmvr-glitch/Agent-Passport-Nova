# Submission Checklist

This checklist captures the release gate for the Agent Passport submission.

## Required artifacts

- [ ] `passport.yaml` is present and matches the current agent identity and travel metadata.
- [ ] `passport-travel-evidence-signed.json` exists and verifies successfully.
- [ ] `red-team-report.json` exists and shows the safe red-team suite in PASS status.
- [ ] `demo.py` runs successfully in a clean environment.
- [ ] `python -m pytest -q` passes with zero skipped tests.

## Security checks

- [ ] Optional security dependency installed: `pip install -e ".[security]"`.
- [ ] Optional dev/test dependency installed: `pip install -e ".[dev]"`.
- [ ] No plaintext private keys are committed to the release tree.
- [ ] No high-confidence live secrets are present in application/config files.
- [ ] Encryption and signing flows are present and verified.

## Release sign-off

- [ ] Verified demo output shows `PASSPORT VERIFIED ✓`.
- [ ] Verified security audit status is PASS.
- [ ] Final submission notes are recorded in project docs and release artifacts.
