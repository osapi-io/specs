## 1. Record the capability

- [x] 1.1 Verify each rule against the code rather than the documentation
  stating it
- [x] 1.2 Write the `sdk-standards` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Point the sources at the capability

- [ ] 2.1 `osapi` — `docs/docs/sidebar/sdk/guidelines.md` keeps its worked
  examples and points at the capability for the rules
- [ ] 2.2 `osapi` — `CLAUDE.md` drops the SDK naming block, which the capability
  now states

## 3. Verification

- [ ] 3.1 Confirm no service method repeats its service name
- [ ] 3.2 Confirm no public signature contains a generated type
- [ ] 3.3 Confirm every exported result field carries a JSON tag
- [ ] 3.4 Confirm no consumer imports the generated package
