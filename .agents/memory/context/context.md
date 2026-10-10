# Base HUB - Context Index

Load the smallest file that fits the task.

## Primary files

- `backend-context.md`: backend runtime, storage, workflow, RBAC, multi-db, bootstrap.
- `frontend-context.md`: SPA/view behavior, widget contracts, workflow canvas, mobile/markdown rules.
- `website-module-context.md`: website-module planning, reuse points, static-publishing architecture.
- `knowledge-module-context.md`: knowledge-module doc-tree architecture and content search (Postgres FTS / filesystem JSON fallback).
- `module-lifecycle-context.md`: module install/uninstall/reinit/scan lifecycle, module selection resolution, manifest/folder identity rules, masterdata-vs-install-state split.
- `base-mcp-context.md`: the `/mcp` JSON-RPC gateway — tool/call API behavior and fixes.
- `masterdata-import-context.md`: master-data import/reinit semantics, esp. secret-field handling on reimport.
- `base-bus-context.md`: the `base-bus` service-bus module (backend + frontend) — transport, cross-import rules, bus-pushed client actions.
- `base-auth-activation-context.md`: `modules/base-auth`'s activation-with-code primitive.
- `edc-module-context.md`: the `edc` module (EDC terminal device registry) — scaffold shape, non-`base-`-prefixed auto-install exclusion.
- `coding-rules.md`: backend implementation guardrails.
- `frontend-coding-rules.md`: frontend implementation guardrails.
- `css-requirement.md`: Tailwind-first styling and responsive checks.

## Repo roots

- `app/backend/`: backend app root.
- `app/backend/internal/`: kernel, runtime, routes, services, commands.
- `app/backend/modules/`: module-owned models, data, security, views, routes.
- `app/backend/frontend/`: SPA app root (static, no-bundler Owl app, embedded from source; serves `/` and `/web/*`).
- `app/backend/frontend/modules/`: module-scoped frontend features.
- `.agents/memory/planning/`: plans and execution notes.
- `.agents/memory/review/`: review notes.
- `.agents/knowledge/SRS/`: as-built SRS documents.
- `CHANGELOG.MD` (repo root): release history, semver, currently `v0.0.1`. Update via base-product's Changelog mode, never by hand-editing prior entries.

## Build

- Root `make build` runs `build:new-admin` + `build:be` (Go build) only. No pnpm/Node build step exists anywhere.
- `app/frontend-admin` (React/Vite) was deleted 2026-10-01 along with `make build:admin` and the `../frontend-admin/dist` disk candidate in `resolveStaticAssets`. The `/admin` route still exists and serves only an optional legacy `./public` tree (also used for module `static/**` lookups and by `conf03`'s injected `EmbeddedAssets.Static`). `// Port of frontend-admin's ...` headers in `app/backend/frontend` and knowledge SRS docs are history notes; the referenced paths no longer exist.

## Configuration rule (repo-wide, 2026-10-01)

- Every required runtime setting (secrets, keys, feature switches) must be set under `Config > app`
  in the YAML config (`internal/config.AppSettings`, read via `config.Config.App.<Field>`). Never read
  runtime settings with `os.Getenv`/`os.LookupEnv`, and don't re-add `viper.AutomaticEnv()`.
- Adding a field: struct field with `mapstructure:"snake_case" yaml:"camelCase"`, plus entries in
  `canonicalConfigKeySegment` and `camelConfigKeySegment`, plus `config.yaml` and `config_dev.yaml`.
  Use `*bool` when an absent key must default to true.
- Exempt: test-harness env switches (`internal/test`, `*_test.go`: `BASE_HUB_RUN_DB_INTEGRATION_TESTS`,
  `RUNTIME_GRAPH_TEST_DB_*`, `EDC_TEST_DATABASE_URL`, `CONF_REQUIRE_DB`).
- Current `app` keys: `encryptKey`, `edcProvisioningEnable`, `discussInboundWebhookSecret`.
- File-only keys (2026-10-03, `internal/config/config_file_only.go`): `app.encrypt_key` is never
  seeded into / read from / persisted via `sys.config_param` (purged at home-DB sync; DB->Config and
  DB->YAML paths overlay it from the loaded file). Tracked yaml holds `encryptKey: ""`; production
  gets it from masked CI var `BASEHUB_ENCRYPT_KEY`, injected by `make deploy` into the remote
  config.yaml (mode 600) — never into build/ (a CI artifact). Add future secrets to `fileOnlyConfigKeys`.
- `LoadConfig` logs Config with `%+v`; EncryptKey is redacted there, other secrets (DB password etc.) are not yet.

## Git workflow

- `base-edc` branch: when cherry-picking/committing to this branch, never include code from the `database` or `helpdesk` modules.
- MQTT source of truth is `base-edc`, not `dev` (user directive, 2026-10-04): MQTT kernel/transport changes (`internal/services/mqtt/`, `route_mqtt.go`, MQTT parts of base-workflow/base-bus) are made on `base-edc` first and cherry-picked to `dev` and other editions under the same title; on other branches diff against `base-edc` before touching MQTT. Playbook: `.agents/skills/base-hub/references/mqtt.md`.
- Split commits by EDC ownership (user directive, 2026-10-03): when committing, put changes under
  `app/backend/frontend/modules/edc/**` and `app/backend/modules/edc/**` in their own commit
  (`[UPDATE] edc: ...`), and commit everything else (core frontend, `internal/`, `services/`,
  `.agents/`, other modules) in a separate commit. Never mix EDC module paths with non-EDC paths in
  one commit, even when they belong to the same feature — commit the shared/core change first, then
  the EDC commit that depends on it.

## Load rule

- Start here, then load one focused file.
- Load both backend and frontend context only for cross-stack work.
- Prefer `*-coding-rules.md` for implementation style; `*-context.md` for behavior, invariants, and regressions to avoid.
- For ChatGPT Custom GPT / GPT Actions / Apps / custom MCP app docs, use `base-product` and load `/home/jean/agents/skills/base-product/references/chatgpt-custom-gpt.md`.

## Pinned `@thebase/ui` version

- `@thebase/ui@1.1.2` (1.0.0 bumped 2026-10-03, first stable, semver from here — same exports/registry/templates/icons as 0.0.12; 1.0.0 → 1.1.1 on 2026-10-04, → 1.1.2 on 2026-10-06). `app/backend/frontend/index.html` is the ONLY pin (CSS, min.js,
  importmap); `main.js` derives templates.xml + icons from `import.meta.resolve("@base/owl")` — never hardcode the
  version there again (an ESM/templates version skew crashes with `Cannot find the definition of component "Icon"`).
  After a bump, stamp `frontend/version.json` so the service worker purges cached index.html/main.js. Reuse this exact version for CDN URLs, registry/icon lookups
  (`dist/baseui.registry.json`, `dist/icons/lucide.json`) and any new frontend work.
- 0.0.12 contract notes: `TabsList` is a shadcn pill list (`.bu-tabs-list`, no `nav nav-tabs`, already
  no-wrap + `overflow-x:auto` — don't add `flex-nowrap overflow-auto`); `TabContent` has no Card chrome
  (opt in via your own wrapper/`className`). `Toast` lays out `.bu-toast-content` + `.bu-toast-actions`
  natively — put extra buttons in `<t t-set-slot="action">`, don't re-flex the toast in app CSS.
- 1.0.0 notes: `Component` from `@base/owl` now falls back to globally registered BaseUI components, so a
  missing `static components` entry no longer crashes nested components (own entries still win). `.bu-sidebar-menu`
  is now `flex:1;min-height:0;overflow-y:auto` — only scrolls when its parent has a bounded height; this app's
  menus sit in auto-height groups inside the `ShellNav` scroller, so no nested scrollbars.
- 1.1.x notes: browser global is now `window.thebase` (same object as deprecated `window.BaseUI`, removed in 2.0.0) —
  use `window.thebase?.mountAll(...)` / `window.thebase.icons.lucide`, never reintroduce `window.BaseUI`. 1.1.0 adds a
  standalone `dist/baseui.analytics.*` tracker; 1.1.1 only adds `visitorContext()` to it. Main bundles/templates/CSS unchanged.

## `app/` = aPuppet web-admin port on BaseUI (2026-10-10)

- `app/` is a no-bundler Owl PWA (index.html, app.js/xml/css, manifest, sw.js) pinned to `@thebase/ui@1.1.2` in `index.html` importmap + `baseui.pwa.config.mjs`.
- `create-baseui-app` is not on npm: regenerate `manifest.webmanifest`/`sw.js` by calling `buildManifest`/`buildServiceWorker` from `dist/baseui.pwa.esm.js` (manifest is an object — `JSON.stringify` it). Config must be `.mjs`.
- `app/` now re-implements `web-admin/` (jQuery/Bootstrap 4/toastr/bootbox + gulp) as an Owl app: `js/*.js` are ES-module ports (store, remote-chat/video/session, commands, gestures, monitoring, cheat codes, debug); `js/lib/{janus,adapter}` stay classic scripts (globals). One `Root` component + `app.xml` sub-templates; shared reactive `state` in `js/store.js` (mutate only through that proxy, components `useState(state)`).
- Deploy contract: `settings.js` next to `index.html` must define `janusServers`, `apiSecret`, `janusDebugLevel`, `streamingOpaqueId`, `textroomOpaqueId` (see `settings.example.js`). The existing `deploy/templates/web-admin/settings.js.j2` still works via the `window.toastr` stub in `index.html`; Makefile/nginx/deploy still point at `web-admin/` (not yet switched). Paths are relative (nginx serves under `/web-admin/`).
- Janus server popup: `js/janus-config.js` — user choice in `localStorage["apuppet.janus"]` ({servers[], apiSecret}) overrides settings.js defaults; popup (`state.janusDialog`) opens when no server is configured, on Janus `error`, or via the footer "Server settings" link; settings.js globals are read via `window.*` so a missing settings.js does not crash.
- Gotchas: scaffold's `stripTemplatesWrapper` only matched bare `<templates>` — fixed to `<templates[^>]*>` (app.xml root has `xml:space`). Owl template compiler trims `&#160;` — use spans/margins. BaseUI `Input` has no `maxlength` (limit in `onInput`), `Button` has fixed height (override with `.bu-button.btn-start`), Bootstrap 5 `.row > *` is width:100% (use `d-flex` for inline rows), `.col-md-auto` needs `position-relative` for the gesture overlay. `Toast` only shows after `open` flips true post-mount (see `Notice`). Headless test: playwright 1.49 + chromium needs libatk/asound extracted via `apt-get download` + `LD_LIBRARY_PATH` (no root).
