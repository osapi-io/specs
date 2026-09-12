# Go version

A repository supports the two most recent Go minor releases. The `go` directive
in `go.mod` names the older of those two, because the directive is a floor: it
is the oldest Go a consumer may build with. Naming the newest release instead
drops support for the one before it, which is the opposite of the rule.

The directive moves when a new minor release lands, not when someone notices. Go
releases a minor roughly every six months, so the value is wrong for months
before anything reminds anybody, and each repository drifts to a different
number in the meantime.

Nothing is written down here about which release is current. The answer is what
the module proxy's toolchain list returns, the same way the repository set is
what `gh repo list` returns. A version recorded in a document is right the day
it is written and wrong after the next release, with nothing marking the moment.

Tool provisioning tracks the latest release rather than this floor. The two
answer different questions: the floor is what a consumer must have, and the
provisioned version is what this repository's own checks run against. A
contributor builds with the newest Go while the module still admits the one
before it.
