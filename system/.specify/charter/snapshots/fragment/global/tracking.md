# Tracking

An issue records that something should change. A specification records what
changing it means, and a task list records the order it is built in. These are
stages of one piece of work, not three records of it: an issue is closed by the
pull request that implements the specification it became, and a task is never
mirrored into an issue, which is why `speckit-taskstoissues` is not used.

An issue exists so an intent survives being put down. Work under way is tracked
by its task list, which is authoritative while it runs; copying it into issues
produces a second list that drifts from the first and is read by whoever finds it
first.

An issue is opened in the repository the change lands in, never in the design
record, because that is where the reader of the code looks. Work spanning the
organization therefore reads issues alongside pull requests and alerts, and an
intent nobody wrote down as one is work nobody can find.

Something exploitable is never an issue. An issue is public the moment it is
opened, so it is reported as a draft advisory on the repository it affects.
