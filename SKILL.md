# SKILL: point_to Target Resolution
 
## Overview
 
When a user says "point to X", the MCP layer must decide HOW to resolve X
into RA/Dec coordinates before sending to the backend. Two resolvers exist:
 
- **JPL Horizons** — for solar system bodies (planets, moons, comets, Sun)
- **Simbad + astropy** — for deep sky objects (nebulae, galaxies, clusters, stars)
Classification and payload construction are handled by Claude itself via the
tool's docstring — no hardcoded lists, no separate API calls, no hardcoded
observer coordinates. Claude asks the user for their location if needed.
 
---
 
## Decision Flow
 
```
User: "point to ____"
           │
           ▼
  Claude reads tool docstring
  and classifies target using
  its own astronomical knowledge
           │
     ┌─────┴──────┐
     │             │
  SOLAR_SYSTEM   DEEP_SKY
  (planet/moon/  (nebula/galaxy/
   comet/Sun)     cluster/star)
     │             │
     ▼             │
  Does Claude know       │
  the user's location?   │
     │                   │
    No → Ask user        │
     │                   │
    Yes                  │
     │                   │
     ▼             ▼
 JPL Horizons    Simbad
 input_body      input_body
 (with location) (no location needed)
     │             │
     └─────┬───────┘
           ▼
   POST /point  {target, resolver, input_body}
           │
           ▼
        Backend
```
 
---
 
## Observer Location
 
Location is **never hardcoded**. Claude is responsible for obtaining it.
 
The Horizons `location` block requires:
- `lon` — longitude in decimal degrees
- `lat` — latitude in decimal degrees
- `elevation` — elevation above sea level in kilometres
**How Claude gets it:**
- If the user mentioned a city or coordinates earlier in the conversation, Claude uses that.
- If not, Claude **stops and asks** before calling the tool:
  *"What is your location? (city or coordinates, and approximate elevation)"*
- Claude converts city names to decimal lon/lat using its own knowledge.
- If elevation is not provided, `0.0` is used as a safe default.
**Simbad does not need a location** — deep sky object coordinates are fixed
in space and do not depend on the observer's position.
 
---
 
## Payload Formats
 
### Solar System → JPL Horizons
 
```json
{
  "target": "Jupiter",
  "resolver": "horizons",
  "input_body": {
    "id": "Jupiter",
    "location": {
      "lon": <user longitude as float>,
      "lat": <user latitude as float>,
      "elevation": <user elevation in km as float>
    },
    "epochs": "Time.now().jd",
    "id_type": "majorbody"
  }
}
```
 
- `id` — the body name or JPL numeric ID (e.g. "599" for Jupiter)
- `location` — populated from user's actual location, never hardcoded
- `epochs` — Julian Date; backend resolves `"Time.now().jd"` at request time
- `id_type` — `"majorbody"` for planets/moons; `"smallbody"` for asteroids/comets
### Deep Sky → Simbad
 
```json
{
  "target": "Orion Nebula",
  "resolver": "simbad",
  "input_body": {
    "name": "Orion Nebula"
  }
}
```
 
- `name` — any string Simbad understands: common names, Messier (M42), NGC, IC catalog IDs
- Backend calls `Simbad.query_object(name)` and applies astropy precession
  to convert J2000 coordinates to the current epoch before slewing
---
 
## Classification Logic
 
Classification is performed by Claude using its own astronomical knowledge,
guided by the tool's docstring. No hardcoded body lists exist in the codebase.
 
**Rule:**
- Solar system body (planet, moon, comet, asteroid, dwarf planet, Sun) → `"horizons"`
- Anything outside the solar system (nebula, galaxy, cluster, star) → `"simbad"`
- Unknown or ambiguous targets default to `"simbad"` — Simbad returns a clean
  error for unrecognised names, which is easier to debug than a wrong resolver.
**Why Claude instead of a hardcoded list?**
A static list can never cover every asteroid, newly discovered moon, or unusual
phrasing. Claude's astronomical knowledge handles "Apophis", "67P", "a comet
near Mars", or any future discovery without any code changes.
 
---
 
## Examples
 
| User says | Resolver | Notes |
|---|---|---|
| "Jupiter" | horizons | majorbody, needs location |
| "Moon" | horizons | majorbody, needs location |
| "Apophis" | horizons | smallbody (asteroid), needs location |
| "67P" | horizons | smallbody (comet), needs location |
| "Orion Nebula" | simbad | no location needed |
| "M31" | simbad | no location needed |
| "Andromeda Galaxy" | simbad | no location needed |
| "Betelgeuse" | simbad | star outside solar system |
 
---
 
## Backend Contract (what the backend team must implement)
 
`POST /point` accepts:
 
```json
{
  "target":     string,
  "resolver":   "horizons" | "simbad",
  "input_body": { ... }
}
```
 
Backend responsibilities:
- If `resolver == "horizons"`: call JPL Horizons with `input_body`, get RA/Dec
- If `resolver == "simbad"`: call `Simbad.query_object(input_body["name"])`,
  apply astropy precession to current epoch, get RA/Dec
- Slew the mount to the resulting RA/Dec
- Return `{ "job_id": "...", "status": "running" }`
The MCP layer guarantees:
- `resolver` is always `"horizons"` or `"simbad"`, never anything else
- Horizons payloads always contain a `location` block with `lon` and `lat`
- Location values always come from the user, never hardcoded defaults
---
 
## Files Involved
 
| File | Role |
|---|---|
| `tools/point_to.py` | MCP tool — docstring instructs Claude; validates payload; calls backend_client |
| `target_classifier.py` | Defines `TargetType` enum only — no classification logic |
| `backend_client.py` | `point_to(target, resolver, input_body)` — forwards to `POST /point` |