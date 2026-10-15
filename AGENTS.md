# osclive – notes for AI agents

An OSC server (TCP, OSC 1.0 framing, port **4301**, plus Zeroconf) for remote control of PreSonus StudioLive mixers. This is a **fork** of [martinspinler/osclive](https://github.com/martinspinler/osclive). The fork adds basic support for the **StudioLive 24.4.2 over FireWire**, the mixer of the Mennonitengemeinde Basel-Holee. In production it runs on the livestreaming PC as the user service `osclive.service`, inside the `python_venv` toolbox (Fedora Silverblue, **Python 3.13**), started as plain `osclive` (raw1394 backend, no config file). It is used for the automatic audio switching during the Sunday service.

## Layout

- `osclive/__main__.py` → CLI (`-u` Universal Control host, `-m` MIDI port, `-c` YAML config with channel names, `-d` debug). It picks the backend; **the raw FireWire backend is hardcoded to `StudioLive2442` in this fork** (upstream used the 16.0.2).
- `osclive/handler.py` → OSC address space (`/channel/<ch>/<control>`, `/channel/<ch>/label`, `/init`, level/peak and `/connection_ping` feedback).
- `osclive/osc/server.py` → TCP server, Zeroconf registration.
- `osclive/studiolive/` → `remote.py` (`SLRemote`), backends (`rawbackend.py` + `raw.py` for raw1394/MIDI, `ucbackend.py` + `uc.py` for Universal Control), device maps `studiolive1602.py` and `studiolive2442.py`.
- `tools/topyg.py` → TouchOSC layout generator.
- `pyproject.toml` → entry point `osclive`; `pip install '.[dev]'` pulls in `raw1394` (pyraw1394 from git), MIDI and YAML. mypy settings are there too.

## The 24.4.2 support

- `studiolive2442.py` reuses the 16.0.2 control maps (`SL1602CtrlsIn_raw1394` etc.) with 24.4.2 channel offsets: `ch1..ch24`, `sub1..4`, `aux1..10`, `fxa`/`fxb`, `main`. The 24.4.2 status block (`SL2442Status_raw1394`) is still empty; only its length matters.
- All of this is **reverse-engineered**. Only what production uses is known to work, mainly `/channel/ch<N>/mute` (0 = unmuted, 1 = muted) on ch 3, 7 and 15. Treat everything else as unverified, and say so instead of assuming that a control maps correctly.
- Reverse-engineering helpers (FireWire trace dumps, index finders) live as untracked local files here and in `livestreaming-pc-infra`. They are not part of the package.

## Conventions

- Keep the upstream code style (type hints, mypy-clean, `%`-formatting where the surrounding code uses it). Keep fork changes small and localized (e.g. device-specific maps in their own module), so that merging from upstream stays easy and an upstream PR remains possible.
- Bump `version` in `pyproject.toml` only when asked.
- There are no tests. Without the mixer, at most `python -m osclive --help` and imports can be checked; FireWire access needs the hardware.

## Safety

- On the PC, osclive writes **directly into the mixer's registers**. A wrong write can mute or change the live sound during the service. Don't send OSC messages to `192.168.71.139:4301`, don't run experimental register writes against the mixer, and don't restart the service, without asking.

## Sibling repos

On the dev machine, the related repos are checked out next to this one in `~/dox/src/` (`../<name>/`).

| Sibling | Interface with this repo |
| :--- | :--- |
| `livestreaming-pc-infra` | Deploys this repo (from the `master` branch of the GitHub URL, `pip_args: '.[dev]'`), the systemd unit `templates/osclive.service.j2`, firewall port 4301, FireWire udev rule. Its script `roles/sw_setup/files/scripts/trigger_audio_scene` sends `oscsend osc.tcp://…:4301 /channel/ch<N>/mute i <0\|1>`. Changing that address scheme or the channel names breaks it. |
| `slidegen` | No direct link. The CD recording takes the same mixer signal through the PipeWire source `studiolive_main_mix`, which is configured in `livestreaming-pc-infra`. |
| `technik-dokumentation` | Full technical documentation (German). Read its `AGENTS.md` (section map) first, then only the relevant sections of `home.md`, never the whole file. Most relevant: `### Die Licht- und Audioautomation mit VulcanBoard erklärt` (which channels are switched when). |

Rules:

* When changing the OSC address space, channel naming or startup behavior, check `livestreaming-pc-infra` (`grep -rn 'oscsend\|osclive' ../livestreaming-pc-infra/roles ../livestreaming-pc-infra/templates`) and make the matching change, or explicitly say what needs to change there.
* Read siblings selectively, never whole repos.
* If a sibling is not checked out, say so instead of guessing its interface.

## Workflow

* **NEVER commit or push.** Leave all git history operations to the user.
* When a change is done, suggest a commit message following Conventional Commits,
  **unscoped** (`feat!: ...`, `feat: ...`, `fix: ...`, `chore: ...`, `doc: ...`, `refactor: ...`),
  lowercase, imperative, matching `git log`. If the change spans several repos, suggest
  one message per repo.
