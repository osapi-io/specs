# osapi-lab

`osapi-lab` is a small fleet of real machines that runs whatever osapi checkout
you point it at. One Mac is the hub, Tart VMs on it run an agent each, and one
command builds your osapi branch, uncommitted changes included, and restarts
everything on it. It is where osapi gets restarted and new builds get pushed
out, by hand, before anything is released.

It holds no Go and ships nothing. Its content is Ansible roles and playbooks
that `uv` runs, Packer templates for the VM images, and a justfile that calls
them.

## The shape

```
            Mac (hub)                        your machine on the tailnet
   ┌──────────────────────────┐           ┌──────────────────────────────┐
   │ osapi nats server :4222  │◄──────────│ uv run ansible-playbook      │
   │ osapi controller  :8080  │ Tailscale │ osapi client, agent (macos)  │
   └────────────▲─────────────┘           └──────────────────────────────┘
                │ vmnet, the subnet's .1
     ┌──────────┼───────────┐
 ubuntu-1    debian-1    fedora-1        Tart VMs, one agent each
```

The hub runs osapi's embedded NATS server and the controller as launchd agents,
and each VM as a launchd agent of its own running `tart run`, so the fleet comes
back when the hub reboots. Each VM runs `osapi-agent` under systemd. Agents dial
out to NATS, so nothing needs a route into a VM: a VM reaches the hub at its
vmnet subnet's `.1`, and a remote machine reaches it by its tailnet name.

Ansible runs on your machine, not on the hub. It reaches the hub over SSH and
each VM by jumping through the hub, so the hub needs no checkout of this
repository.

```
ansible/
  pyproject.toml, uv.lock   the ansible package, pinned; uv installs and runs it
  ansible.cfg               inventory = inventory.yml, roles_path = roles
  inventory.example.yml     committed: the shape of an inventory
  inventory.yml             gitignored: the hub, its tailnet name, the checkout
  group_vars/all.yml        committed: the VMs, a name and a base image each
  playbooks/                site, push, secrets, hub, images, vms, agents, client
  roles/
    build                   compiles the osapi checkout, on your machine
    secrets                 the lab's secrets and the VMs' SSH key, once
    hub                     osapi's NATS server and controller on the hub
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

`ansible/inventory.yml` is the only file that names a machine. It is gitignored
and starts as a copy of `inventory.example.yml`, the way k3s-ansible keeps
`inventory-sample.yml`. The VM names in `group_vars/all.yml` are committed,
since they name nothing outside the lab.

## How to run it

Everything goes through `just`. Each lab recipe is one call to
`just ansible-run <playbook>`, which the `ansible` module from
[osapi-justfiles](../osapi-justfiles/README.md) defines: it runs
`uv run ansible-playbook playbooks/<playbook>.yml` from `ansible/`, where
`ansible.cfg` is.

`uv` supplies the Ansible pinned in `ansible/uv.lock`, so a person and an agent
run the same version. Nothing calls `ansible-playbook` from the path, for the
same reason osapi's agents never call `go build` directly: the version on the
path is whatever somebody happened to install. The same module gives
`ansible-lint`, `ansible-fmt` and `ansible-test`, which `just test` runs.

| Recipe        | Playbook     | Does                                                  |
| ------------- | ------------ | ----------------------------------------------------- |
| `just list`   | `list.yml`   | Every VM, its image and its osapi build; changes none |
| `just push`   | `push.yml`   | Rebuild the fleet from your osapi checkout            |
| `just deploy` | `deploy.yml` | Copy your build into the hub and the running VMs      |
| `just site`   | `site.yml`   | Everything, from nothing                              |
| `just ssh vm` | `client.yml` | Refresh `.lab/ssh/config`, then `ssh -F` through it   |

`.lab/ssh/config` holds a `Host` per VM with its current address and a jump
through the hub, so `ssh`, `scp` and `rsync` reach a VM with `-F`. It includes
`~/.ssh/config`, since `-F` replaces it and the hub may be an alias defined
there.

## How a build reaches the fleet

`playbooks/push.yml` rebuilds the fleet from your checkout:

- **`build`** compiles the osapi checkout the inventory names, for darwin and
  linux on arm64, on your machine. It builds the UI first, because osapi embeds
  `ui/dist`. It records the branch, the commit and whether the tree was dirty in
  `.lab/bin/REVISION`, so the lab always says which build it runs.
- **`hub`** copies the darwin build to the hub, re-admits it through the
  firewall, and restarts the NATS and controller agents.
- **`images`** bakes the linux build into an image per distribution, named
  `img-<distro>-<tag>`. The tag is the build's short commit, with `-dirty` when
  the checkout had uncommitted changes, so the hub's image list says which osapi
  each image holds. A clean tag whose image exists is not rebuilt; a dirty one
  always is, since its contents can change under the same commit. Images from
  other builds are deleted.
- **`vms`** deletes each VM, clones it again from its new image, and adds it to
  the inventory.
- **`agents`** drops each VM's config in and starts its agent.

Each VM is then exactly its image plus a config. That takes minutes, mostly
Packer booting each image once. `playbooks/deploy.yml` is the quick loop: it
copies the build into the hub and the running VMs and leaves the images alone,
so a VM runs a build its image does not hold until the next push.

## Why it is built this way

**A real host, not a container.** osapi's `just behavior-int-linux` runs a
behavior's examples against an agent in one Debian container, which is enough to
show that a provider does what its examples say. It cannot show what an operator
sees: several agents answering one broadcast, a distribution osapi does not
support, a Mac agent skipping almost everything, a restart under systemd. The
lab shows those.

**Ansible, not a justfile of shell.** The first version was bash in the
justfile: a render script for templates, an scp loop for the VMs, a sudo check
written by hand, and a copy of the repository on the hub so recipes could run
there. Ansible has each of those as a module, makes every step safe to run
twice, and keeps the VMs in an inventory. The cost is a Python toolchain, which
`uv` reduces to one lock file. Running Ansible through `uv` from a justfile is
what pytorch's `ci-infra` does for its runner fleet.

**The image holds osapi, never its config.** A VM rebuilt from its image runs
exactly the build that went in, rather than whatever was last copied onto it.
The config carries the NATS password, so it stays out: Ansible drops it in after
the clone, the way Mozilla's macos-vms has the Tart host supply a VM's
credentials at boot rather than bake them in.

**Packer still builds the images.** No Ansible collection drives Tart. The
`packer` role copies `packer/` to the hub and runs it there, because Tart runs
only on the Mac that holds the VMs. The `tart_vm` role drives Tart with plain
commands and `add_host`, the way every public Ansible-and-Tart setup does.

**Small roles, composed.** `packer`, `tart_vm`, `launchd` and `firewall` know
nothing about osapi and take their inputs as variables. The osapi roles use
them, and the playbooks only list roles.

**A launchd agent per VM, not a daemon.** Tart keeps VMs under the user's home,
and a launchd daemon starts with no `HOME`. An agent in the user's session has
it, and `KeepAlive` restarts a VM that stops.

**Build where you edit.** The checkout that changes is on your machine, so the
build happens there and only binaries move.

**An image says what it is.** Packer writes the image's name and the build's
description to `/etc/osapi-lab/image`, and `list.yml` reads it from each VM
beside `osapi version`, so what a VM runs is a lookup, not a guess.

**Every clone gets its own machine ID.** osapi identifies an agent by
`/etc/machine-id`. The image ships that file empty, so systemd writes a new one
on each clone's first boot.

**Secrets never enter an image or the repository.** They are generated once on
your machine, into `.lab/`, and the hub and each VM receive only their rendered
config. An agent's config carries a throwaway signing key rather than the hub's,
because osapi validates every key in the file, whatever the command.

## What will surprise you

**`-K` asks for the hub's sudo password.** The hub's macOS firewall admits a
binary by its code signature, and every build has a new one, so each push
re-admits it. The VMs need no password; their account has passwordless sudo.

**A binary is never overwritten in place.** macOS kills a signed binary whose
bytes change while it runs. Ansible's `copy` writes a temporary file and renames
it over the target, which gives the new binary its own inode.

**Fedora runs with `IGNORE_LINUX=1`.** osapi's agent exits at startup on a
distribution outside its supported list. The `agent` role sets osapi's own
override in a systemd drop-in on every node that is not Ubuntu or Debian, so the
agent starts, runs the generic Linux providers and skips the rest. Ubuntu and
Debian nodes have the drop-in removed, so the supported-distribution gate still
runs wherever it passes. Both are osapi's `debian` platform, so every behavior
runs on them.

**A config osapi would reject stops the deploy.** The `agent` role runs
`client health liveness` with each rendered config, on your machine with the
darwin build, before shipping it. A command that fails for any other reason,
such as the controller still starting, does not stop it; `invalid config` does.

**The VMs are reachable only through the hub.** They sit on the hub's vmnet
subnet. Ansible jumps through the hub to reach them; nothing on your network can
reach a VM directly.

**Stopping a VM by hand does not keep it stopped.** Its launchd agent restarts
it. Unload the agent to stop a VM for good.

**A push throws away anything done inside a VM.** It reclones every VM.
`deploy.yml` keeps them.

## Where it sits

It depends on osapi as a checkout, not as a module: it builds whatever the
inventory points at. Its justfile fetches the `md`, `just` and `ansible` modules
from [osapi-justfiles](../osapi-justfiles/README.md). Nothing depends on it.

## Not covered here

How to install Tart, set up Tailscale, or answer the first-run prompts. Those
are in osapi-lab's own README, which is the operator's page. This page is what
the lab is and why.
