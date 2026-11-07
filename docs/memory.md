# Memory - durable findings

This file is reserved for conventions, gotchas, and non-obvious facts.
It should not be used as a log of every session or minor change. Entries should be short and prefixed with the date added/edited.

## Naming Conventions

### Domain Entities
- Avoid ambiguous names like `Stream`. Use specific entity names such as `StreamSource` or `QueueStream` to maintain clarity across the codebase. (2026-10-07)


## Backend
### Routing

### Source Metadata
- [2026-11-07] Odysee RSS exposes per-video thumbnails via `itunes:image[href]`; store the URL at fetch time.
- [2026-11-07] CLI `-add` omits `isWeb` and `remoteId`; infer both from YouTube URIs so manual
	QueueStreams receive thumbnail URLs too.

### Filename Sanitization
- [2026-11-07] `grdUtil.sanitize(..., mode=1)` removes punctuation, periods, and underscores.
- Sanitize filename stems only; restore extensions and generated separators afterward.

## Frontend
### Colors & Design System
- [2026-10-04] CSS variables with semantic color names: Onyx (#070D0B), Silver (#B5B5B5), Evergreen (#013D33), Jungle Teal (#02866F), Gold (#D4AF37), and Platinum (#EBEBEB).

### Form UX
- [2026-10-04] WTForms labels should not include "(optional)"; use `render_kw={'placeholder': '...'}` to provide default value hints instead.
