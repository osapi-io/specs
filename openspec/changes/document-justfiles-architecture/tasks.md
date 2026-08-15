## 1. Record the architecture

- [x] 1.1 Survey the modules on `main` to establish what is actually true:
  consumption style, shim presence, documentation location, version pinning
- [x] 1.2 Write the `justfiles` capability describing distribution, consumption,
  naming, documentation, and formatter boundaries
- [x] 1.3 Record the two consumption styles and the shim failure mode as
  scenarios rather than as commentary
- [x] 1.4 Record the decisions and their rejected alternatives in design.md

## 2. Follow-up

Converging on a single consumption style modifies the consumption requirement
recorded here, changes six modules, and breaks every consuming repository as it
lands. It is tracked as its own change.

- [ ] 2.1 Open a change to converge on one consumption style
