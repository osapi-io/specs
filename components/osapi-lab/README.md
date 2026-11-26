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

The API, NATS, Jaeger's UI and its OTLP receiver each serve the hub's Tailscale
certificate, and each connection checks it: the CLI, the controller, each agent
and each exporter. The certificate names the tailnet name only. Thus a
connection that dials `127.0.0.1` or the `.1` address of the subnet sets
`server_name` to the tailnet name. Plain text to any of the four is refused.
[TLS](../osapi/configuration.md#tls) has the settings.

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
  playbooks/
    lab.yml                 each workflow: a mode, the VMs and the parts of the run
    list, logs, teardown    read the lab, or remove it from the hub
    build, client           the build and the configs of this machine alone
    lock, unlock            the lock, which each other playbook takes
  roles/
    build                   compiles the osapi checkout for each OS that the run needs
    secrets                 the lab's secrets and the VMs' SSH key, kept, and the admin token, renewed
    client                  the configs on your machine
    hub_tls                 the hub's Tailscale certificate, which the hub's processes serve
    hub_host                what NATS and the controller share: directories, the build, hub.yaml
    nats_server             osapi's NATS server on the hub
    controller              the controller on the hub, with the API and the UI
    jaeger                  the trace collector on the hub
    lab_images              bakes the image of each VM that needs one
    lab_vm                  clones one of the lab's VMs, mapped onto tart_vm
    vm_inventory            adds each running VM to the inventory
    lab_agent               a new build into a running VM's agent, or a restart
    fleet_ready             waits until each agent is Ready, and a new process after a restart
    nats_consumers          removes the consumers of agents that are gone
    packer                  builds a Packer template on a host      (generic)
    tart_vm                 one Tart VM: clone, launchd, stop, start (generic)
    tart_base               a local base image from a disk image    (generic)
    launchd                 one launchd agent: run, stop, start     (generic)
    firewall                admits one app through the macOS firewall (generic)
    lock                    the lock of the hub                     (generic)
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

| Recipe          | Mode      | Does                                                         |
| --------------- | --------- | ------------------------------------------------------------ |
| `just deploy`   | `deploy`  | Bake each image that changed, replace its VM, update the hub |
| `just bump`     | `bump`    | Put a new build into each running process; bake no image     |
| `just rebuild`  | `rebuild` | Bake each image again and replace each VM                    |
| `just restart`  | `restart` | Restart each process; no build and no copy                   |
| `just stop`     | `stop`    | Stop each process and VM, so that launchd does not start it  |
| `just start`    | `start`   | Start what `stop` stopped                                    |
| `just list`     |           | Every VM, its image and its osapi build; changes none        |
| `just ssh vm`   |           | Refresh `.lab/ssh/config`, then `ssh -F` through it          |
| `just teardown` |           | Remove the lab from the hub                                  |

Each recipe with a mode runs `playbooks/lab.yml`. The recipe gives it three
things:

- `lab_mode`, the mode of the table.
- `lab_only`, a comma list of VMs. Empty is each VM.
- the tags of the parts: `nats`, `controller`, `jaeger`, `vms` and `client`.
  With no tag, each part runs.

The recipe makes these from its targets. `ui` is `controller`, because osapi
embeds the UI. `hub` is `nats`, `controller` and `jaeger`. A VM's name goes to
`lab_only` and adds `vms`. Thus `just deploy ui` builds darwin, copies it to the
hub, restarts the controller alone, and waits for each agent.
`just rebuild debian-lts` bakes the image of one VM and clones it again. The
lock, a check of the run, the build and the secrets run on each run.

`group_vars/all.yml` turns the mode into what the run does to each VM of the
run. `lab_replace_vms` get an image and a clone, `lab_update_vms` get a new
build, and `lab_restart_vms` restart:

| Mode      | Replaced              | Updated                     | Restarted |
| --------- | --------------------- | --------------------------- | --------- |
| `deploy`  | each, when it changed | each that upgrades in place | none      |
| `bump`    | none                  | each                        | none      |
| `rebuild` | each                  | none                        | none      |
| `restart` | none                  | none                        | each      |

A process on the hub restarts only when it is a part of the run, and only when a
file that it reads at its start is not the file that it started on, or in a
`restart`. The files are its binary, `hub.yaml`, the certificate and its key,
and the NATS auth. NATS also reads the JetStream key, and Jaeger its own binary
and config. When a process starts, the `launchd` role records a checksum of
these files in `~/.osapi-lab/run/<process>.inputs`. Each run compares the files
with that record. Thus a run on the controller leaves NATS as it is, and the
next run on NATS restarts it if the controller's run changed its binary or
`hub.yaml`.

`teardown` reverses `deploy` on the hub. It does these steps:

- It stops each `io.osapi.lab.*` launchd agent, Jaeger included, and deletes its
  plist.
- It deletes the `lab-*` VMs.
- It removes the firewall entries for the osapi build and for Jaeger.
- It deletes the state directory of the hub, but for `images/`.

It keeps two things that are slow or impossible to make again:

- the `img-*` images that the VMs clone from, and `~/.osapi-lab/images/`, which
  has the fingerprint that each image was baked from. Without the fingerprint,
  the next `deploy` bakes each image again. `-e lab_teardown_images=true`
  deletes both.
- the `.lab` of this machine, which has the NATS operator and its keys.
  `-e lab_teardown_local=true` deletes it.

If you delete the operator, each credential that it gave stops working. Thus the
next `deploy` makes a new operator.

`.lab/ssh/config` has a `Host` for each VM, with its current address and a jump
through the hub. Thus `ssh`, `scp` and `rsync` get to a VM with `-F`. It
includes `~/.ssh/config`, because `-F` replaces it, and the hub can be an alias
that is defined there.

## How a build reaches the fleet

`just deploy` brings the fleet to your checkout. `lab.yml` runs its roles in
this order:

- **`build`** compiles the osapi checkout that the inventory names, on your
  machine. It always builds darwin, which this machine and the hub run. It
  builds linux only when the run reaches a VM. It builds the UI first, because
  osapi embeds `ui/dist`. Each OS records the branch and the commit, and if the
  tree had changes, in `.lab/bin/<os>.REVISION` and `<os>.TAG`. It also records
  a fingerprint of the source in `<os>.FINGERPRINT`: the commit, the uncommitted
  diff and the untracked files. An OS whose fingerprint did not change is not
  built again. Thus `just deploy ui` takes about 30 seconds.
- **`hub_tls`**, **`hub_host`**, **`nats_server`**, **`controller`** and
  **`jaeger`** bring the hub to the build. `hub_host` copies the darwin build,
  renders `hub.yaml`, and admits the build through the firewall again. Each of
  the other three runs its process under launchd, and restarts it only as the
  last section says.
- **`lab_images`** bakes an image for each VM of the run, with the name
  `img-<vm>-<tag>`. The image is the whole VM: the linux build, its config, its
  join string, its hostname and each package that a behavior runs, such as
  Docker and chrony. The tag is the short commit of the linux build. It ends
  with `-dirty` when the checkout had uncommitted changes. The fingerprint of an
  image is the fingerprint of the build and a hash of `packer/`. The hub keeps
  it, and builds an image again only when the image is missing or the
  fingerprint is different. Before a build, the role makes a join token for the
  VM, which admits one agent, because the join string goes into the image. The
  token expires in `lab_join_expires`, 24 hours: a VM that is cloned again from
  an older image cannot join, and `just rebuild <vm>` bakes a new one. A run on
  each VM deletes the images from other builds, except an image that a build
  recorded in the last hour. A run on some VMs deletes none, because the other
  VMs run from theirs. It does not bake an image for a VM that upgrades in place
  while that VM exists.
- **`lab_vm`** deletes the admission of a VM and clones it again when its image
  changed. It clones a VM that upgrades in place only when the VM does not
  exist.
- **`vm_inventory`** adds each running VM to the inventory, in the groups that
  the run acts on.
- **`lab_agent`** copies the linux build to `/usr/local/bin/osapi` on each VM
  that the run updates. It restarts `osapi-agent` when the agent runs a binary
  that a copy replaced, which `/proc/<pid>/exe` shows as deleted. Thus a run
  that stopped after the copy and before the restart leaves the restart to the
  next run. In a `restart`, it only restarts the agent.
- **`fleet_ready`** waits until the controller reports each agent of the run as
  `Ready`. For an agent that `lab_agent` restarted, it waits for a process with
  a new `started_at`. If an agent does not come back in 3 minutes, the run
  fails.
- **`client`** writes the configs on your machine, and **`nats_consumers`**
  removes the consumers of agents that are gone.

Each VM, except `debian-lts`, is then exactly its image. When the source or
`packer/` changed, this takes some minutes. Most of the time is Packer, which
boots one VM for each image. When nothing changed, a deploy changes nothing.
`just rebuild` bakes each image again and replaces each VM, also with no change.

`bump` is the fast path for a change to the osapi binary. It builds, puts the
binary on the hub and into each running VM, restarts each process whose binary
changed, and waits for each new agent process to be Ready. It bakes no image and
clones no VM. The first bump took 100 seconds, where a deploy takes about twenty
minutes (osapi-io/osapi-lab#70). A VM then runs a build that is not in its
image, until the next deploy. Thus a `bump` that reaches a VM refuses to run
when `packer/` changed since the image of a VM of the bump was baked.
`lab_images` records the checksum of `packer/` for each VM, in
`~/.osapi-lab/images/<vm>.packer.sum`, when it bakes the VM's image or finds the
image current. A run that bakes some VMs records only theirs, so the other VMs
keep the record of their own image. A change of `packer/`, such as the config of
an agent, needs `deploy` of the VMs that the refusal names. A VM that upgrades
in place is not checked, because only `rebuild` bakes it again.

Only one run at a time changes the images and the VMs. `lab.yml`, `build.yml`
and `teardown.yml` take a lock on the hub, `~/.osapi-lab/lock`, with one
`mkdir`. The lock names its holder: the machine, the process of
`ansible-playbook`, the build and the start time. A second run says which run
holds the lab, and waits for it, for up to `lab_lock_wait` minutes (30). It
fails only then. The wait is one shell loop, because Ansible prints each try of
an `until` loop as `FAILED - RETRYING`, which reads as an error while the lab is
only busy. A playbook that a run imports takes the lock that the run holds, and
the outermost playbook gives it back. On 22 November 2026, two runs at once
deleted the images of each other, because each run deletes the images that its
own build does not clone (osapi-io/osapi-lab#38).

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
exactly what went into it: the build, the config, the join string and the
packages. Nothing configures a VM after it boots, so a VM cannot drift from its
image. The cost is one image for each VM, not one for each distribution, and an
image that holds the join string of its VM. The images are local Tart images on
the hub and never leave it. The owner decided this in osapi-io/osapi-lab#29.

**The image is written in HCL.** `packer/lab.pkr.hcl` uses only the provisioners
of Packer: `file` copies each file in, and `shell` runs short `inline` steps.
`templatefile()` renders the config of the agent from
`packer/agent.yaml.pkrtpl.hcl`. A difference between distributions is a map in
`locals`, such as the Docker package. The join string is a `sensitive` variable,
and the playbook passes it in `PKR_VAR_join`. Thus it is in no argument list and
no log.

**Packer still builds the images.** No Ansible collection controls Tart. The
`packer` role copies `packer/` to the hub and runs it there, because Tart runs
only on the Mac that has the VMs. The `tart_vm` role controls Tart with plain
commands and `add_host`, as each public Ansible-and-Tart setup does.

**A role for each part, and one playbook that puts them together.** Each process
of the lab has its own role, with `main`, `stop` and `start` tasks:
`nats_server`, `controller`, `jaeger`, and `tart_vm` for a VM. Thus a run
targets one part, and a restart, a stop or a deploy of one part leaves the
others as they are. Before, each workflow was a playbook of its own with the
same ten imports, the hub restarted NATS and the controller together, and no VM
could be bumped or rebuilt alone. `packer`, `tart_vm`, `tart_base`, `launchd`,
`firewall` and `lock` know nothing about osapi, and take their inputs as
variables. The osapi roles use them.

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
`just rebuild debian-lts` bakes its image again and replaces it, so a person can
reset it. `fleet_ready` and `nats_consumers` check it as they check the other
VMs (osapi-io/osapi-lab#49).

**Each clone gets its own machine ID.** osapi identifies an agent by
`/etc/machine-id`. The image ships that file empty. Thus systemd writes a new
one on the first boot of each clone.

**Secrets never go into the repository.** The lab makes them one time on your
machine, in `.lab/`. The hub gets its rendered config. Each image gets the
config and the join string of its own VM.

The admin token is the exception to "one time". osapi signs a token for three
months. Thus each run of the `secrets` role checks `.lab/secrets/token` with
`osapi controller token validate` against the current signing keys, and reads
`exp` from the token. The role sends the token on standard input, as
`--token -`, because a secret flag refuses a literal value. Before, the check
failed on each run, so each run signed a new token and restarted the controller.
The role signs a new token when the token is missing, when the keys refuse it,
or when it expires within `secrets_token_renew_days`, 14 by default. A new token
uses the same key, thus the hub needs no change. The CLI, the client of the hub
and the web UI all send this token.

`lab_signing_keys` in `group_vars/all.yml` is the list of signing keys, as
`controller.api.security.signing_keys` takes it. It has one key, `lab`, from
`.lab/secrets/signing_key`. A token that has no `kid`, such as a token from
before the list, fails the check. Thus the next run of the role signs a new
token with the `kid` of `lab`.

The controller keeps the signing keys in its vault, as an operator does, and
`hub.yaml` refers to them as `secret://default/jwt-signing-key-<id>`. The
controller resolves the references at its start. The controller role writes each
key with `osapi client secret update`, from standard input, when the vault does
not hold it. The first run after a teardown starts the controller with the keys
themselves, writes them, and then starts it again on the references
(osapi-io/osapi-lab#54). A NATS password and the key of a vault cannot be a
reference, because osapi needs them before it reads a vault.

`cli.yaml` on your machine holds the keys themselves. Thus
`osapi controller token generate` on your machine signs a token that the
controller accepts. The config of an agent holds no signing key, only its join
string. Thus a VM holds no key that can sign an admin token.

## NATS in operator mode, and the join

The hub runs the NATS server of osapi in operator mode, the decentralized JWT
model of NATS. The hub makes its auth one time with osapi itself:

```bash
osapi nats auth operator create --out ~/.osapi-lab/nats
```

It writes the operator, osapi's account, the resolver file of the server, the
scoped signing keys of the join, and a credentials file for each osapi role with
the least permissions of the role. `hub.yaml` names them. The keys stay on the
hub. A teardown removes them, and the next deploy makes new ones. The design is
in osapi's [transport](../osapi/transport.md#who-may-connect) page.

| User       | Used by                                       | From                               |
| ---------- | --------------------------------------------- | ---------------------------------- |
| setup      | the server's own setup and heartbeat          | `nats/setup.creds` on the hub      |
| controller | the controller, and the `nats` CLI of the lab | `nats/controller.creds` on the hub |
| each agent | the agent of one VM, or the remote agent      | minted by the controller at a join |

A VM joins as a host of an operator does. `lab_images` makes a join token for
each image with `osapi controller join token create --uses 1`, and the image
bakes only its join string, in `agent.join`. The agent joins at its first boot:
the token admits it, and the controller mints its NATS user. `auto_admit` is
off, so a request with no token waits for a person. The remote agent,
`just agent`, joins with a token of its own, whose join string dials the tailnet
name.

The join string of a VM dials the gateway of tart's network, `192.168.64.1`. The
certificate of the hub names its tailnet name, and a CA that the VM trusts
issued it. Thus after the join the agent checks that name against the roots of
the VM, and a renewal of the certificate changes nothing (osapi-io/osapi#1491).

The `nats` CLI in the lab directory connects as the controller. It reads the
lab's streams, buckets and consumers. It cannot delete a consumer, and the lab
has no system user, so the server-wide reports of `nats server` do not work.
Before, `nsc` made an operator on your machine, a user for each VM and a system
user. The lab no longer uses `nsc`.

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
