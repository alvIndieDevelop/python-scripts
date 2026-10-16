# WebWrap Agent Guide

## Scope

WebWrap 0.3.0 is a Python application that creates, lists, opens, edits, and deletes
Chromium web apps through a GTK4/Libadwaita interface. Its stable CLI creates, lists,
launches, and deletes apps. It targets Arch Linux and standard freedesktop launchers,
including launchers commonly used with Hyprland.

Phase 3 management includes graphical open, edit, and confirmed deletion. Graphical
icon selection and isolated-profile selection are still pending. Favicon retrieval,
multiple browsers, release packaging, profile cleanup, and compositor-specific
integration remain deferred unless explicitly requested.

## Technical Baseline

- Python 3.10 or newer.
- Standard-library-only core; the GUI uses system PyGObject, GTK 4.8+, and
  Libadwaita 1.5+.
- Setuptools package with a `src/` layout.
- Console entry points: `webwrap = webwrap.main:main` and
  `webwrap-gui = webwrap.gui:main`.
- Tests use the standard-library `unittest` framework.
- User documentation is Spanish; code, docstrings, comments, and this guide are
  English.

## Package Responsibilities

- `src/webwrap/paths.py`: derives WebWrap and application-entry paths from
  `XDG_DATA_HOME`, falling back to `~/.local/share`.
- `src/webwrap/validation.py`: validates names, HTTP(S) URLs, IDs, and icon files;
  generates path-safe IDs and atomically copies managed icons.
- `src/webwrap/models/webapp.py`: defines the immutable, serializable `WebApp`
  boundary and validates records loaded from storage.
- `src/webwrap/services/app_store.py`: loads, validates, and atomically replaces the
  versioned JSON application database.
- `src/webwrap/services/browser.py`: resolves Chromium, builds shell-free argument
  lists, creates isolated profiles on first launch, and starts the browser.
- `src/webwrap/services/desktop_entry.py`: renders freedesktop entries and atomically
  writes mode `0644` launcher files under the XDG applications directory.
- `src/webwrap/operations.py`: coordinates create, open, update, delete, and rollback
  behavior for both frontends.
- `src/webwrap/main.py`: defines CLI syntax, translates expected failures into concise
  CLI errors, and coordinates multi-artifact creation and deletion with rollback.
- `src/webwrap/gui.py`: checks graphical dependencies before loading GTK modules.
- `src/webwrap/application.py`: owns the Libadwaita application lifecycle.
- `src/webwrap/window.py`: displays the application list and coordinates graphical
  create, open, edit, and confirmed-delete actions.
- `src/webwrap/dialogs.py`: collects add/edit input and presents validation errors.

## Core Invariants

- Treat CLI values and persisted JSON as untrusted input. Validation must also occur
  when data crosses the model or filesystem boundary.
- Application IDs must remain compatible with
  `^[a-z0-9]+(?:-[a-z0-9]+)*$` before they are used in any path.
- URLs must remain restricted to `http` and `https`, include a hostname, and contain
  no whitespace or control characters.
- Launch Chromium with an argument list and without a shell. Do not convert browser
  arguments into shell command strings.
- Desktop-entry `Exec` values follow freedesktop escaping rules. They are not shell
  commands and must not use shell quoting helpers such as `shlex.quote`.
- Replace managed JSON, icons, and desktop entries atomically within the destination
  filesystem. Flush file contents before replacement where the current services do.
- Desktop entries remain regular `0644` files; they do not need executable bits.

## Data Consistency and Deletion

- Never overwrite malformed, unsupported, or schema-invalid `apps.json`. Surface an
  `AppStoreError` so the user can recover the original data.
- CLI operations that affect the database, icon, and desktop entry must preserve the
  existing best-effort rollback behavior when an intermediate step fails.
- Delete an icon only when its resolved parent is the managed icons directory, its
  stem exactly matches the application ID, and its suffix is supported.
- Deleting an application removes its database record, desktop entry, and managed
  icon. It must preserve isolated Chromium profile data.
- Isolated profile directories are created only when the application is opened.
- Keep user-visible success output stable and minimal: `Created <id>` and
  `Deleted <id>`. An empty list prints `No web apps configured.`.

## Coding Conventions

- Follow PEP 8 with a maximum line length of 100 characters.
- Prefer `pathlib.Path` for filesystem paths.
- Add type hints to new and changed code.
- Write docstrings and comments in English. Comments should explain non-obvious
  reasons rather than restate operations.
- Catch and translate specific exceptions at service boundaries. Avoid broad
  `except Exception` handlers that hide programming errors.
- Preserve the package/service architecture and the minimal subcommand CLI; do not
  apply the parent repository's interactive-menu or emoji-heavy script template.
- Keep `gi` imports out of core modules so CLI and core tests work without GTK.
- GTK widgets must call shared operations and services rather than writing JSON,
  copying icons, or generating desktop entries themselves.
- Make the smallest correct change and avoid unrelated refactors.
- Do not modify or duplicate the parent `LICENSE` file.

## Change Workflow

1. Read `pyproject.toml` and the affected modules and tests before editing.
2. Add or update focused `unittest` coverage for behavior changes.
3. Update `README.md` whenever public CLI behavior, supported inputs, XDG paths, or
   deletion semantics change.
4. Run the complete validation set from this directory:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m webwrap --help
webwrap-gui --help
```

5. Exercise lifecycle operations against temporary data instead of the user's real
   XDG directories:

```bash
tmp_data="$(mktemp -d)"
XDG_DATA_HOME="$tmp_data" python -m webwrap create \
  --name "Agent Test" \
  --url "https://example.com"
XDG_DATA_HOME="$tmp_data" python -m webwrap list
XDG_DATA_HOME="$tmp_data" python -m webwrap delete APP_ID
rm -rf "$tmp_data"
```

Use the ID emitted by `create` for the delete step. Browser launch validation requires
a graphical session and Chromium, so keep it separate from headless lifecycle checks.

## Repository Hygiene

Do not commit any of the following:

- `.venv/` or another local virtual environment.
- `__pycache__/`, `*.pyc`, coverage output, build output, or `*.egg-info/`.
- User `apps.json`, copied icons, isolated browser profiles, or any other XDG data.
- Generated `webwrap-*.desktop` entries.

Before finishing, inspect the diff and confirm that only files required by the task
changed. Preserve unrelated work already present in the worktree.
