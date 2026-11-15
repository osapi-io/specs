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
   │ jaeger            :4317  │           └──────────────────────────────┘
   └────────────▲─────────────┘
                │ vmnet, the subnet's .1
     ┌──────────┼───────────┐
 ubuntu-1    debian-1    fedora-1        Tart VMs, one agent each
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
to an agent. The UI listens on `127.0.0.1:16686`, on the hub only.

Ansible runs on your machine, not on the hub. It gets to the hub over SSH, and
to each VM through the hub. Thus the hub needs no checkout of this repository.

```
ansible/
  pyproject.toml, uv.lock   the ansible package, pinned; uv installs and runs it
  ansible.cfg               inventory = inventory.yml, roles_path = roles
  inventory.example.yml     committed: the shape of an inventory
  inventory.yml             gitignored: the hub, its tailnet name, the checkout
  group_vars/all.yml        committed: the VMs, a name and a base image each
  playbooks/                site, push, secrets, hub, images, vms, agents, client,
                            teardown
  roles/
    build                   compiles the osapi checkout, on your machine
    secrets                 the lab's secrets and the VMs' SSH key, once
    hub                     osapi's NATS server, controller and Jaeger on the hub
    lab_vm                  one of the lab's VMs, mapped onto tart_vm
    agent                   one VM's agent: config, IGNORE_LINUX, restart
    client                  the client config on your machine
    packer                  builds a Packer template on a host      (generic)
    tart_vm                 one Tart VM: clone, launchd, add_host   (generic)
    launchd                 one launchd agent                       (generic)
    firewall                admits one app through the macOS firewall (generic)
packer/                     the images: OS preparation and the osapi binary
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
| `just push`     | `push.yml`     | Rebuild the fleet from your osapi checkout            |
| `just deploy`   | `deploy.yml`   | Copy your build into the hub and the running VMs      |
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

`playbooks/push.yml` builds the fleet again from your checkout:

- **`build`** compiles the osapi checkout that the inventory names, for darwin
  and linux on arm64, on your machine. It builds the UI first, because osapi
  embeds `ui/dist`. It records the branch, the commit, and if the tree had
  changes, in `.lab/bin/REVISION`. Thus the lab always tells which build it
  runs. It also makes a fingerprint of the source: the commit, the uncommitted
  diff and the untracked files. If nothing changed since the last build, it
  skips the build.
- **`hub`** copies the darwin build to the hub, admits it through the firewall
  again, and restarts the NATS and controller agents.
- **`images`** puts the linux build into an image for each distribution, with
  the name `img-<distro>-<tag>`. The tag is the short commit of the build. It
  ends with `-dirty` when the checkout had uncommitted changes. Thus the image
  list of the hub tells which osapi each image has. The hub keeps the
  fingerprint of each image. It builds an image again only when the image is
  missing or the fingerprint is different. Thus a tree with changes gets a new
  image only when it changed again. It deletes images from other builds.
- **`vms`** clones a VM again when its recorded image and fingerprint are
  different from what it must run. It adds each VM to the inventory.
- **`agents`** puts the config of each VM in place, and starts its agent.

Each VM is then exactly its image and a config. When the source changed, this
takes some minutes. Most of the time is Packer, which boots each image one time.
When the source did not change, a push changes nothing.

`playbooks/deploy.yml` is the fast loop. It copies the build into the hub and
the running VMs, and does not change the images. Thus a VM runs a build that its
image does not have, until the next push.

## Why it is built this way

**A real host, not a container.** `just behavior-int-linux` in osapi runs the
examples of a behavior against an agent in one Debian container. That shows that
a provider does what its examples say. It cannot show what an operator sees:

- many agents that answer one broadcast
- a distribution that osapi does not support
- a Mac agent that skips almost everything
- a restart under systemd

The lab shows those.

**Ansible, not a justfile of shell.** The first version was bash in the
justfile. It had a render script for templates, an scp loop for the VMs and a
sudo check written by hand. It also needed a copy of the repository on the hub,
for the recipes that ran there. Ansible has a module for each of those. It makes
each step safe to run two times, and keeps the VMs in an inventory. The cost is
a Python toolchain, and `uv` reduces that to one lock file. pytorch runs Ansible
through `uv` from a justfile for the runner fleet of its `ci-infra`.

**The image has osapi, never its config.** A VM that you build again from its
image runs exactly the build that went into it. It does not run the last file
that somebody copied onto it. The config and the NATS credentials of the VM stay
out of the image. Ansible puts them in after the clone. In the same way, the
macos-vms project of Mozilla has the Tart host give the credentials of a VM at
boot, and does not put them in the image.

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

**Each clone gets its own machine ID.** osapi identifies an agent by
`/etc/machine-id`. The image ships that file empty. Thus systemd writes a new
one on the first boot of each clone.

**Secrets never go into an image or the repository.** The lab makes them one
time on your machine, in `.lab/`. The hub and each VM get only their rendered
config. The config of an agent has a temporary signing key, not the key of the
hub, because osapi validates each key in the file for each command.

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

Each user is made where it is deployed, by
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

**`-K` asks for the hub's sudo password.** The macOS firewall of the hub admits
a binary by its code signature. Each build has a new signature, so each push
admits the binary again. The VMs need no password. Their account has
passwordless sudo.

**A binary is never overwritten in place.** macOS kills a signed binary whose
bytes change while it runs. Ansible's `copy` writes a temporary file and renames
it over the target, which gives the new binary its own inode.

**Fedora runs with `IGNORE_LINUX=1`.** The agent of osapi stops at startup on a
distribution that is not on its supported list. On each node that is not Ubuntu
or Debian, the `agent` role sets the override of osapi in a systemd drop-in.
Thus the agent starts, runs the generic Linux providers and skips the others.
The role removes the drop-in from Ubuntu and Debian nodes. Thus the check for
supported distributions still runs where it passes. The two are the `debian`
platform of osapi, so each behavior runs on them.

**A config that osapi refuses stops the deploy.** Before the `agent` role sends
a rendered config, it runs `client health liveness` with it, on your machine,
with the darwin build. `invalid config` stops the deploy. A failure for a
different reason does not stop it, for example a controller that has not started
yet.

**The VMs are reachable only through the hub.** They sit on the hub's vmnet
subnet. Ansible jumps through the hub to reach them; nothing on your network can
reach a VM directly.

**Stopping a VM by hand does not keep it stopped.** Its launchd agent restarts
it. Unload the agent to stop a VM for good.

**A push after a source change throws away anything done inside a VM.** It
reclones every VM whose image changed. `deploy.yml` keeps them.

## Where it sits

It depends on osapi as a checkout, not as a module: it builds whatever the
inventory points at. Its justfile fetches the `md`, `just` and `ansible` modules
from [osapi-justfiles](../osapi-justfiles/README.md). Nothing depends on it.

## Not covered here

How to install Tart, configure Tailscale, or answer the first-run prompts. The
README of osapi-lab has those, and it is the page for the operator. This page
tells what the lab is and why.
