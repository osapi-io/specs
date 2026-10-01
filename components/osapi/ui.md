# The embedded UI

osapi ships a React single-page application compiled into the controller binary.
There is no separate deployment, no second process and no extra port: the built
assets go into the Go binary through `//go:embed`, and the controller serves
them from the same host and port as the REST API.

```yaml
controller:
  ui:
    enabled: true # default
```

Setting it false makes the controller skip registering the SPA handler and serve
only the REST API. That is the one thing about the UI an operator acts on.

## Its API client is generated from the same specification as the Go SDK

Not a hand-written client, and not a second specification. `orval` generates it
from the combined OpenAPI file that the Go SDK also generates from, so **an
endpoint added to a domain reaches both** without anybody writing TypeScript.

A fetch mutator adapts the generated client for the browser, which is where the
bearer token is attached.

So the UI ships inside osapi's binary rather than being deployed beside it.

## The four kinds of component

What separates them is **what each one knows and whether it renders**, not what
it is called. A new file goes where those two answers put it.

| Kind             | Knows                           | Lives in                    |
| ---------------- | ------------------------------- | --------------------------- |
| primitive        | no osapi resource               | `ui/src/components/ui/`     |
| domain component | exactly one osapi resource      | `ui/src/components/domain/` |
| layout           | none; it holds page chrome      | `ui/src/components/layout/` |
| hook             | a resource, and renders nothing | `ui/src/hooks/`             |

So: markup with one resource is a domain component, a resource with no markup is
a hook, and markup with no resource is a primitive unless it is page chrome,
which is a layout. Primitive and layout are the pair the knowledge column cannot
separate, because neither knows a resource; what separates them is that a
primitive is reused anywhere and a layout exists to position pages.

The hook rule is enforced by the file extension. Every file in `ui/src/hooks/`
is `.ts` rather than `.tsx`, so a hook **cannot** contain markup.

## Authentication, and the asymmetry worth knowing

The UI uses the same JWT the rest of osapi uses. A token comes from
`osapi token generate`, is pasted into the sign-in page or supplied through the
environment, and is sent as a bearer header on every request.

**The UI decodes that token without verifying it.** It reads the roles claim to
decide what to show. Verification is the server's job, and the server does it on
every request.

A contributor who read only the client would take the decode for a check. It is
not one. Nothing the UI hides is protected by the UI hiding it.

Its permission model is osapi's, not a second one. The roles claim it reads
resolves through the same 37 permissions and three roles the API checks,
described in [permissions](permissions.md). What each role permits for an
*operator* is also on the published site, where somebody configuring one will
look.

## Coverage says nothing about it

`/ui/` is in `.coverignore`, so osapi's coverage figure excludes the UI
entirely. A contributor who assumed the gate covered it would be wrong, and
nothing in the gate's output says so.

The UI's correctness rests on its own checks: `just react-lint`,
`just react-test` and the Docusaurus build for its documentation.

## Where this connects

What the generated client is generated *from*, and why a domain absent from the
combined specification is invisible to it, is [building a domain](domains.md).

______________________________________________________________________

Written from `ui/` and `internal/controller/api/ui/`.
