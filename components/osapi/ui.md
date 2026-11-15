# The embedded UI

osapi ships a React single-page application inside the controller binary. There
is no separate deployment, no second process and no additional port. The build
puts the assets into the Go binary through `//go:embed`. The controller serves
them from the same host and port as the REST API.

```yaml
controller:
  ui:
    enabled: true # default
```

If you set it to false, the controller does not register the SPA handler. It
serves only the REST API. This is the only UI setting that an operator changes.

## Its API client is generated from the same specification as the Go SDK

Nobody writes the client by hand, and there is no second specification. `orval`
generates it from the combined OpenAPI file. The Go SDK comes from the same
file. Thus **an endpoint that you add to a domain goes to the two clients**, and
nobody writes TypeScript for it.

A fetch mutator changes the generated client for the browser. It attaches the
bearer token.

## The four kinds of component

Two answers separate the kinds: **what each one knows, and if it renders**. The
name does not separate them. Put a new file where those two answers put it.

| Kind             | Knows                           | Lives in                    |
| ---------------- | ------------------------------- | --------------------------- |
| primitive        | no osapi resource               | `ui/src/components/ui/`     |
| domain component | exactly one osapi resource      | `ui/src/components/domain/` |
| layout           | none; it holds page chrome      | `ui/src/components/layout/` |
| hook             | a resource, and renders nothing | `ui/src/hooks/`             |

Thus:

- Markup with one resource is a domain component.
- A resource with no markup is a hook.
- Markup with no resource is a primitive. If it is page chrome, it is a layout.

The knowledge column cannot separate a primitive from a layout, because neither
knows a resource. A primitive can be used again in any location. A layout exists
to put pages in position.

The file extension enforces the hook rule. Each file in `ui/src/hooks/` is
`.ts`, not `.tsx`. Thus a hook **cannot** contain markup.

## Authentication, and the difference to know

The UI uses the same JWT as the rest of osapi. A token comes from
`osapi token generate`. You paste it into the sign-in page, or you give it
through the environment. The UI sends it as a bearer header on each request.

**The UI decodes that token, but it does not verify it.** It reads the roles
claim to decide what to show. The server verifies the token on each request.

A contributor who reads only the client can think that the decode is a check. It
is not a check. When the UI hides something, that does not protect it.

The sign-in page refuses two kinds of token before it keeps one.
`checkTokenFormat` in `ui/src/lib/token-format.ts` refuses a token that has
whitespace, a character outside base64url, or a number of parts that is not
three. The page does not remove the bad character. A token that the terminal
wrapped gets a space at the line break, and `atob` ignores that space. The
server does not ignore it, and it returns 401 to each request. Thus the page
tells the person to copy the token again.

Then the page sends one request, `GET /api/health/status`, with the new token. A
401 means that the server refused the token, for example because a different
signing key made it. The page shows the reason from the server and does not keep
the token. Any other status means that the server accepted the token, and the
page keeps it. This is the verification of the server, not of the UI. The server
still checks each request after sign-in.

A token in `localStorage` from an earlier session gets no check. If the server
refuses it, each page shows an error until the person signs out.

The permission model of the UI is the model of osapi. There is not a second
model. The roles claim uses the same 37 permissions and three roles that the API
checks. [Permissions](permissions.md) describes them. The published site also
tells what each role permits for an *operator*, because a person who configures
a role looks there.

## Coverage says nothing about it

`/ui/` is in `.coverignore`. Thus the coverage figure of osapi does not include
the UI. The gate does not cover the UI, and nothing in the output of the gate
says so.

The UI has its own checks: `just react-lint`, `just react-test` and the
Docusaurus build for its documentation.

## Where this connects

[Building a domain](domains.md) tells what the client comes *from*. It also
tells why the client cannot see a domain that is not in the combined
specification.

______________________________________________________________________

Written from `ui/` and `internal/controller/api/ui/`.
