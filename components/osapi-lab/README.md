# osapi-lab

`osapi-lab` is a small fleet of real machines. It runs the osapi checkout that
you point it at. One Mac is the hub. Tart VMs on it run one agent each. One
command builds your osapi branch, with the uncommitted changes, and restarts all
of the fleet on it. People restart osapi and send new builds here, by hand,
before a release.

It has no Go and ships nothing. Its content is:

- Ansible roles and playbooks that `uv` runs
- Packer templates for the VM images
- a justfile that calls them

## The shape

```
            Mac (hub)                        your machine on the tailnet
   ┌──────────────────────────┐           ┌──────────────────────────────┐
   │ osapi nats server :4222  │◄──────────│ uv run ansible-playbook      │
   │ osapi controller  :8080  │ Tailscale │ osapi client, agent (macos)  │
   │ jaeger     :4317, :16686 │           └──────────────────────────────┘
   └────────────▲─────────────┘
                │ vmnet, the subnet's .1
     ┌──────────┼───────────┬────────────┐
 ubuntu-1    debian-1    fedora-1    debian-lts    Tart VMs, one agent each
```

The hub runs the embedded NATS server of osapi, the controller and Jaeger as
launchd agents. Jaeger is the native darwin-arm64 binary from its release,
pinned by checksum. Thus the hub needs no Docker. Each VM is also a launchd
agent that runs `tart run`. Thus the fleet starts again when the hub reboots.
Each VM runs `osapi-agent` under systemd. Agents connect out to NATS. Thus
nothing needs a route into a VM. A VM gets to the hub at the `.1` address of its
vmnet subnet. A remote machine gets to the hub by its tailnet name.

Each process sends its traces to Jaeger on the hub, over OTLP gRPC on 4317:

- the controller to `127.0.0.1`
- the agent of a VM to the `.1` address of the subnet
- a remote agent to the tailnet name

There is one collector, because one trace goes from the controller through NATS
to an agent. The UI listens on `0.0.0.0:16686`, as the controller listens on
`0.0.0.0:8080`. Thus you open both from a machine on the tailnet, at the tailnet
name of the hub. The UI has no authentication. Each machine on the LAN and on
the vmnet bridge can also read the traces. The lab accepts that, because the
tailnet and the LAN have one user. A remote agent does not change this, because
it only sends spans.

The hub writes these locations into the `url` keys of its config:
`controller.api.url`, `controller.ui.url`, `telemetry.tracing.url` and
`nats.server.url`. Thus `osapi client health status` shows a location that you
can open, next to the bind address. [Observability](../osapi/observability.md)
has the `url` field. The tailnet name comes from `lab_hub_addr` in
`inventory.yml`, which git ignores. Set `lab_controller_url`,
`lab_tracing_view_url` or `lab_nats_url` in the inventory to show a different
location. The metrics servers answer the hub only, thus they get no `url`.

Ansible runs on your machine, not on the hub. It gets to the hub over SSH, and
to each VM through the hub. Thus the hub needs no checkout of this repository.

```
ansible/
  pyproject.toml, uv.lock   the ansible package, pinned; uv installs and runs it
  ansible.cfg               inventory = inventory.yml, roles_path = roles
  inventory.example.yml     committed: the shape of an inventory
  inventory.yml             gitignored: the hub, its tailnet name, the checkout
  group_vars/all.yml        committed: the VMs, a name and a base image each
  playbooks/                site, rebuild, deploy, secrets, hub, images, vms, ready,
                            client, teardown
  roles/
    build                   compiles the osapi checkout, on your machine
    secrets                 the lab's secrets and the VMs' SSH key, kept, and the admin token, renewed
    hub                     osapi's NATS server, controller and Jaeger on the hub
    lab_vm                  one of the lab's VMs, mapped onto tart_vm
    client                  the client config on your machine
    packer                  builds a Packer template on a host      (generic)
    tart_vm                 one Tart VM: clone, launchd, add_host   (generic)
    launchd                 one launchd agent                       (generic)
    firewall                admits one app through the macOS firewall (generic)
packer/                     one image for each VM: the whole VM, in HCL
.lab/ (gitignored)          builds, secrets, the VMs' SSH key, rendered configs
```

`ansible/inventory.yml` is the only file that names a machine. git ignores it.
It starts as a copy of `inventory.example.yml`, as k3s-ansible keeps
`inventory-sample.yml`. The VM names in `group_vars/all.yml` are in git, because
they name nothing outside the lab.

## How to run it

All work goes through `just`. Each lab recipe is one call to
`just ansible-run <playbook>`. The `ansible` module from
[osapi-justfiles](../osapi-justfiles/README.md) defines it. It runs
`uv run ansible-playbook playbooks/<playbook>.yml` from `ansible/`, where
`ansible.cfg` is.

`uv` supplies the Ansible version that `ansible/uv.lock` pins. Thus a person and
an agent run the same version. Nothing calls `ansible-playbook` from the path.
The reason is the same as the reason that agents in osapi never call `go build`
directly: the version on the path is the version that somebody installed. The
same module gives `ansible-lint`, `ansible-fmt` and `ansible-test`, which
`just test` runs.

| Recipe          | Playbook       | Does                                                  |
| --------------- | -------------- | ----------------------------------------------------- |
| `just list`     | `list.yml`     | Every VM, its image and its osapi build; changes none |
| `just deploy`   | `deploy.yml`   | Bake the changed images, replace those VMs            |
| `just rebuild`  | `rebuild.yml`  | Bake each image again, replace each VM                |
| `just site`     | `site.yml`     | Everything, from nothing                              |
| `just ssh vm`   | `client.yml`   | Refresh `.lab/ssh/config`, then `ssh -F` through it   |
| `just teardown` | `teardown.yml` | Remove the lab from the hub                           |

`teardown` reverses `site` on the hub. It does these steps:

- It stops each `io.osapi.lab.*` launchd agent and deletes its plist.
- It deletes the `lab-*` VMs.
- It removes the firewall entries for the osapi build and for Jaeger.
- It deletes the state directory of the hub.

It keeps two things that are slow or impossible to make again:

- the `img-*` images that the VMs clone from. `-e lab_teardown_images=true`
  deletes them.
- the `.lab` of this machine, which has the NATS operator and its keys.
  `-e lab_teardown_local=true` deletes it.

If you delete the operator, each credential that it gave stops working. Thus the
next `site` makes a new operator.

`.lab/ssh/config` has a `Host` for each VM, with its current address and a jump
through the hub. Thus `ssh`, `scp` and `rsync` get to a VM with `-F`. It
includes `~/.ssh/config`, because `-F` replaces it, and the hub can be an alias
that is defined there.

## How a build reaches the fleet

`playbooks/deploy.yml` brings the fleet to your checkout:

- **`build`** compiles the osapi checkout that the inventory names, for darwin
  and linux on arm64, on your machine. It builds the UI first, because osapi
  embeds `ui/dist`. It records the branch, the commit, and if the tree had
  changes, in `.lab/bin/REVISION`. Thus the lab always tells which build it
  runs. It also makes a fingerprint of the source: the commit, the uncommitted
  diff and the untracked files. If nothing changed since the last build, it
  skips the build.
- **`hub`** copies the darwin build to the hub, admits it through the firewall
  again, and restarts the NATS and controller agents.
- **`images`** bakes an image for each VM of the inventory, with the name
  `img-<vm>-<tag>`. The image is the whole VM: the linux build, its config, its
  NATS credential, its hostname and each package that a behavior runs, such as
  Docker and chrony. The tag is the short commit of the build. It ends with
  `-dirty` when the checkout had uncommitted changes. The fingerprint of an
  image is the fingerprint of the build and a hash of `packer/`. The hub keeps
  it, and builds an image again only when the image is missing or the
  fingerprint is different. Before a build, the playbook makes the NATS user of
  the VM, because the credential must exist before it goes into the image. It
  deletes images from other builds, except an image that a build recorded in the
  last hour. It does not bake an image for a VM that upgrades in place while
  that VM exists.
- **`vms`** deletes the admission of a VM and clones it again when its image
  changed. It clones a VM that upgrades in place only when the VM does not
  exist. It adds each VM to the inventory.
- **`upgrade`** copies the linux build to `/usr/local/bin/osapi` on each VM that
  upgrades in place. If the binary changed, it restarts `osapi-agent`. Then it
  waits until the controller reports an agent process with a new `started_at`
  that is `Ready`. If the agent does not come back in 3 minutes, the run fails.
- **`ready`** waits until the controller reports the agent of each VM as
  `Ready`. The agent starts at boot with the baked config, and the hub admits
  it. Nothing logs in to a VM.

Each VM, except `debian-lts`, is then exactly its image. When the source or
`packer/` changed, this takes some minutes. Most of the time is Packer, which
boots one VM for each image. When nothing changed, a deploy changes nothing.
`playbooks/rebuild.yml` does the same, but bakes each image again and replaces
each VM, also with no change.

Only one run at a time changes the images and the VMs. `deploy`, `rebuild`,
`site`, `images`, `vms` and `teardown` take a lock on the hub,
`~/.osapi-lab/lock`, with one `mkdir`. The lock names its holder: the machine,
the process of `ansible-playbook`, the build and the start time. A second run
stops with that name. A playbook that a run imports takes the lock that the run
holds, and the outermost playbook gives it back. On 22 November 2026, two runs
at once deleted the images of each other, because each run deletes the images
that its own build does not clone (osapi-io/osapi-lab#38).

A run that stops before its end keeps the lock. The next run on the same machine
finds that the process is gone, and breaks the lock. A lock from a run on a
different machine needs `-e lab_lock_break=true`. Ansible cannot run a step
after a play fails in a different play, so the lock has no release on failure.
The check of the process takes its place.

The lock of one run does not cover the tests after the deploy. Thus a second
deploy can replace the build while the tests of the first still run against it
(osapi-io/osapi-lab#41). A session holds the lock from the deploy through the
end of the tests:

- `just lock <name>` takes the lock for the session `<name>`. It waits while a
  different run or session holds the lock.
- Each recipe that runs with `LAB_SESSION=<name>` is the holder of the lock, so
  it runs, and it keeps the lock when it ends.
- `just unlock <name>` gives the lock back.
- `just lab-session <name> <command>` takes the lock, runs the command with
  `LAB_SESSION` set, and gives the lock back, also when the command fails.

The holder of a session is `session <machine> <name>`. A session that is older
than `lock_session_ttl`, 2 hours, is stale, and the next run breaks it.

## Why it is built this way

**Many real hosts, not one runner.** CI in osapi runs the write examples of each
behavior against one agent on its Ubuntu runner. That shows that a provider does
what its examples say. It cannot show what an operator sees:

- many agents that answer one broadcast
- a distribution that osapi does not support
- a Mac agent that skips almost everything
- a restart under systemd

The lab shows those.

**The same suite, pointed at the lab.** osapi's integration suite runs against
the lab from an osapi checkout. `OSAPI_INTEGRATION_OSAPIFILE` names the lab's
`.lab/config/cli.yaml`, and `OSAPI_INTEGRATION_TARGET` names one VM. The suite
then starts nothing and tests the hub's controller and that VM's agent. With
`OSAPI_INTEGRATION_WRITE_BEHAVIORS=1`, the write examples run on the VM, and the
VM gets its state back after each one. The suite prepares the VM through osapi,
the same as it prepares the CI runner: the ping parameter, chrony, and the dummy
interface `osapi0`. Thus the image does not make `osapi0`, and CI and the lab
run the same suite with no setup outside it. The lab has no recipe of its own
for this: `just go-unit-int` in osapi is the one entry point.

**Ansible, not a justfile of shell.** The first version was bash in the
justfile. It had a render script for templates, an scp loop for the VMs and a
sudo check written by hand. It also needed a copy of the repository on the hub,
for the recipes that ran there. Ansible has a module for each of those. It makes
each step safe to run two times, and keeps the VMs in an inventory. The cost is
a Python toolchain, and `uv` reduces that to one lock file. pytorch runs Ansible
through `uv` from a justfile for the runner fleet of its `ci-infra`.

**The image is the whole VM.** A VM that you build again from its image runs
exactly what went into it: the build, the config, the credential and the
packages. Nothing configures a VM after it boots, so a VM cannot drift from its
image. The cost is one image for each VM, not one for each distribution, and an
image that holds the NATS credential of its VM. The images are local Tart images
on the hub and never leave it. The owner decided this in osapi-io/osapi-lab#29.

**The image is written in HCL.** `packer/lab.pkr.hcl` uses only the provisioners
of Packer: `file` copies each file in, and `shell` runs short `inline` steps.
`templatefile()` renders the config of the agent from
`packer/agent.yaml.pkrtpl.hcl`. A difference between distributions is a map in
`locals`, such as the Docker package. The NATS credential is a `sensitive`
variable, and the playbook passes it in `PKR_VAR_nats_creds`. Thus it is in no
argument list and no log.

**Packer still builds the images.** No Ansible collection controls Tart. The
`packer` role copies `packer/` to the hub and runs it there, because Tart runs
only on the Mac that has the VMs. The `tart_vm` role controls Tart with plain
commands and `add_host`, as each public Ansible-and-Tart setup does.

**Small roles, put together.** `packer`, `tart_vm`, `launchd` and `firewall`
know nothing about osapi, and take their inputs as variables. The osapi roles
use them. The playbooks only list roles.

**One launchd agent for each VM, not a daemon.** Tart keeps VMs under the home
directory of the user. A launchd daemon starts with no `HOME`. An agent in the
session of the user has it. `KeepAlive` restarts a VM that stops.

**Build where you edit.** The checkout that changes is on your machine. Thus the
build occurs there, and only binaries move.

**An image tells what it is.** Packer writes the name of the image and the
description of the build to `/etc/osapi-lab/image`. `list.yml` reads it from
each VM, with `osapi version`. Thus you can read what a VM runs. You do not
guess.

**One VM upgrades in place, on purpose.** Each other VM is a new clone after
each change, with a new machine ID, a new disk and no history. That tests osapi
on a new host, but never the upgrade of a host that ran an earlier build. Two
upgrade bugs reached main on 23 November 2026, and a host with history shows
both:

- the durable consumers of old machine IDs on `osapi-JOBS` grew to the limit of
  1000 and stopped each job (osapi-io/osapi#1154)
- NATS refuses a new deliver policy on a consumer that exists, thus an upgraded
  agent reports `ConsumersUnavailable` (osapi-io/osapi#1181)

Thus `debian-lts` has `upgrade_in_place: true` in `group_vars/all.yml`. It is
cloned one time. After that, each deploy copies the new build into it and
restarts its agent, as an operator upgrades a host. It keeps its machine ID, the
KV records of its agent, its file state, its consumers and its job history. This
breaks the rule that a VM is its image, for one VM only. It keeps the config and
the packages of its first image. A change to `packer/` does not get to it.
`just rebuild` bakes its image again and replaces it, so a person can reset it.
`ready` and `consumers` check it as they check the other VMs
(osapi-io/osapi-lab#49).

**Each clone gets its own machine ID.** osapi identifies an agent by
`/etc/machine-id`. The image ships that file empty. Thus systemd writes a new
one on the first boot of each clone.

**Secrets never go into the repository.** The lab makes them one time on your
machine, in `.lab/`. The hub gets its rendered config. Each image gets the
config and the NATS credential of its own VM.

The admin token is the exception to "one time". osapi signs a token for three
months. Thus each run of the `secrets` role checks `.lab/secrets/token` with
`osapi controller token validate` against the current signing keys, and reads
`exp` from the token. The role signs a new token when the token is missing, when
the keys refuse it, or when it expires within `secrets_token_renew_days`, 14 by
default. A new token uses the same key, thus the hub needs no change. The CLI,
the client of the hub and the web UI all send this token.

`lab_signing_keys` in `group_vars/all.yml` is the list of signing keys, as
`controller.api.security.signing_keys` takes it. It has one key, `lab`, from
`.lab/secrets/signing_key`. A token that has no `kid`, such as a token from
before the list, fails the check. Thus the next run of the role signs a new
token with the `kid` of `lab`.

Two configs hold the signing keys of the hub: `hub.yaml`, which the controller
verifies with, and `cli.yaml` on your machine. Thus
`osapi controller token generate` on your machine signs a token that the
controller accepts. The config of an agent has a temporary signing key, because
osapi validates each key in the file for each command. An agent never signs or
verifies a token. Thus a VM holds no key that can sign an admin token.

A VM that upgrades in place keeps its config. Thus `upgrade.yml` changes the
`signing_key` of its config to a `signing_keys` list before it restarts the
agent. A config with the old key does not load in an osapi that has the list.

## NATS in operator mode

The hub runs the NATS server of osapi in operator mode, the decentralized JWT
model of NATS. An operator who wants credentials for each host does the same. An
operator signs the account of osapi. The account signs a user for each process.
Each process connects with its own credentials file. To add a VM, give it a
credential. The config of the server does not change. The design is in osapi's
[transport](../osapi/transport.md#who-may-connect) page.

| User           | Used by                              | Credentials on                      |
| -------------- | ------------------------------------ | ----------------------------------- |
| `nats`         | the server's own setup and heartbeat | the hub, `secrets/nats.creds`       |
| `controller`   | the controller                       | the hub, `secrets/controller.creds` |
| `agent-<vm>`   | that VM's agent                      | the VM, `/etc/osapi/nats.creds`     |
| `agent-remote` | `just agent` on your machine         | `.lab/secrets/nats/`                |
| `cli`          | the `nats` CLI in the lab directory  | `.lab/secrets/nats/`                |
| `sys`          | `nats-sys`, in the system account    | `.lab/secrets/nats/`                |

`nsc`, which mise pins, makes all of it under `.lab/secrets/nsc`. The `secrets`
role runs, once:

```bash
nsc add operator --name lab --sys --generate-signing-key
nsc add account --name osapi
nsc edit account --name osapi --js-enable 1
```

and on every run, so a changed account reaches the hub:

```bash
nsc generate config --mem-resolver --sys-account SYS --force --config-file .lab/secrets/resolver.conf
```

Each user is made before its image is baked, by
`ansible/roles/secrets/tasks/user.yml`:

```bash
nsc add user --account osapi --name agent-debian-1
nsc generate creds --account osapi --name agent-debian-1 --output-file .lab/secrets/nats/agent-debian-1.creds
```

Every command runs with `--data-dir .lab/secrets/nsc/stores` and with `NSC_HOME`
and `NKEYS_PATH` under `.lab/secrets/nsc`, so the lab's keys never mix with your
own `nsc` setup. The resolver file goes to the hub as `config/resolver.conf`,
which the hub's `nats.server.auth.resolver_file` names.

The users have the account's default permissions for now. Narrowing each agent
to its own subjects and the buckets it uses comes with the least-privilege work.

### Checking it

`.envrc` loads `.lab/config/nats.env`, which `just site` writes, so the `nats`
CLI in the lab directory connects to the hub as `cli`:

```bash
nats account info                 # the cli user, account osapi, JetStream on
nats stream ls                    # osapi's streams, such as JOBS and AUDIT
nats kv ls                        # osapi's buckets, such as job-queue and agent-registry
nats kv ls osapi-agent-registry   # one key per agent that registered
nats sub 'osapi.jobs.>'           # jobs as they go out; run an osapi command elsewhere
NATS_CREDS= nats stream ls        # no credentials: Authorization Violation
```

The last one is the check that matters: a connection without a credential the
account signed is refused.

Server-wide commands need NATS's system account, whose `sys` user `nsc` made
with the operator. `nats-sys` runs the CLI as that user, and plain `nats` stays
the `cli` user:

```bash
nats-sys server list                # the server, its version and connections
nats-sys server report jetstream    # JetStream's streams and storage per account
nats-sys server report connections  # every connection, by account and user
```

`server report connections` shows each osapi process connected as its own user,
which is the check that every credential reached the right place.

## What will surprise you

**The hub needs passwordless sudo.** The macOS firewall of the hub admits a
binary by its code signature. Each build has a new signature, so each rebuild
admits the binary again through sudo. A recipe does not ask for a password. Thus
the user on the hub must have a `NOPASSWD: ALL` rule in `/etc/sudoers.d`. A rule
for one command is not sufficient, because Ansible runs a different command
through sudo each time. The VMs also have passwordless sudo. Thus an agent can
deploy the lab with no person present; [AGENTS.md](../../AGENTS.md#use-the-lab)
says when.

**A binary is never overwritten in place.** macOS kills a signed binary whose
bytes change while it runs. Ansible's `copy` writes a temporary file and renames
it over the target, which gives the new binary its own inode.

**Fedora runs with `IGNORE_LINUX=1`.** The agent of osapi stops at startup on a
distribution that is not on its supported list. The Fedora image has the
override of osapi in a systemd drop-in. Thus the agent starts, runs the generic
Linux providers and skips the others. The Ubuntu and Debian images have no
drop-in. Thus the check for supported distributions still runs where it passes.
The two are the `debian` platform of osapi, so each behavior runs on them.

**A config that osapi refuses stops the build of its image.** The image runs
`client health liveness` with its baked config. `invalid config` stops the
build. A failure for a different reason does not stop it, for example a
controller that the build VM cannot reach.

**The VMs are reachable only through the hub.** They sit on the hub's vmnet
subnet. Ansible jumps through the hub to reach them; nothing on your network can
reach a VM directly.

**A ping from a VM fails while the hub's firewall is in stealth mode.** The VMs
reach the network through the NAT of the hub. In stealth mode, the macOS
firewall drops the ICMP replies to the VMs, but not the replies to the hub's own
pings. Thus each `osapi client node network ping` from a VM, and the `ping` of
the VM, times out, while TCP and DNS from the VM work. Turn stealth mode off on
the hub, or use bridged networking for the VMs. A capture on a VM shows the echo
requests and no replies:

```sh
/usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode   # on the hub
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode off
```

The hub's network can also lose a reply now and then. osapi then reports the
loss, not a failed ping.

**Stopping a VM by hand does not keep it stopped.** Its launchd agent restarts
it. Unload the agent to stop a VM for good.

**A deploy after a change throws away anything done inside a VM.** It reclones
every VM whose image changed, and a rebuild reclones each VM. `debian-lts` is
the exception for a deploy: it keeps its state until a rebuild.

## Where it sits

It depends on osapi as a checkout, not as a module: it builds whatever the
inventory points at. Its justfile fetches the `md`, `just` and `ansible` modules
from [osapi-justfiles](../osapi-justfiles/README.md). Nothing depends on it.

## Not covered here

How to install Tart, configure Tailscale, or answer the first-run prompts. The
README of osapi-lab has those, and it is the page for the operator. This page
tells what the lab is and why.
