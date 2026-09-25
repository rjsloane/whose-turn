# Roadmap

How each planned feature would fit into this codebase. The data model already has
room for most of them, so the plan is mostly to add UI and a storage format bump.

The rule stays the same for every feature: logic in pure modules with tests
(`models.py`, `picker.py`, `storage.py`), and UI in `src/views/`.

## 1. Player photos

**Model:** `Player.photo_path` already exists and is already saved and loaded by `storage.py`.

**Picking from the gallery (no permission needed):**
- Use Flet's `ft.FilePicker()` service:
  `await picker.pick_files(file_type=ft.FilePickerFileType.IMAGE)` returns `FilePickerFile`s with a `.path`.
- Android's system photo picker runs in its own process, so the app needs no storage permission.

**Taking a photo with the camera:**
- `uv add flet-camera` (1.0.1 exists on PyPI). It's a runtime dependency, so it *does* belong in `[project].dependencies`.
- Add the camera permission bundle to `pyproject.toml`:
  ```toml
  [tool.flet]
  permissions = ["camera"]
  ```
  (Equivalent to `flet build apk --permissions camera`.)
- Ask for the permission at runtime before opening the camera. The flet-camera docs recommend `flet-permission-handler` for this, which is another runtime dependency.
- Check the flet-camera docs (flet.dev/docs/controls/camera) for the exact class and method names before writing code.

**Storing photos:**
- Copy the chosen or taken file into the app's own storage. The `FLET_APP_STORAGE_DATA` environment variable points there in a running app.
- Use a file name based on `player.id` (e.g. `photos/<id>.jpg`), so picking a new photo replaces the old one.
- Save the path relative to that folder, not absolute. Android can move app data during restores, so a relative path survives.
- Put this in a new `src/photos.py` with pure path helpers (tested) and one small copy function.

**Showing photos:**
- `views/widgets.py: player_avatar()` is the only place avatars are drawn.
- Change it to use `ft.CircleAvatar(foreground_image_src=...)` when `photo_path` is set, and keep the coloured initial as the fallback.
- Removing a player (`Roster.remove`) should also delete their photo file.

**UI:** tap a player's avatar to get "Choose photo / Take photo / Remove photo", shown in an `ft.BottomSheet` or a dialog.

## 2. Built-in avatars

- **Model:** `Player.avatar` already exists. Store either an emoji (`"🦊"`) or a bundled image key (`"fox"`).
- **Assets:** put images in `src/assets/avatars/` (PNG or SVG). Flet serves `assets/` automatically, so `src="avatars/fox.png"` works, and `flet build` packages it.
- **Choosing one:** a grid of options (`ft.GridView`) in a dialog.
- **Display:** `player_avatar()` picks, in priority order: photo, then built-in avatar, then coloured initial. That rule is pure logic, so it goes in a small function in `models.py` returning e.g. `("photo", path)`, `("avatar", key)` or `("initial", "A")`, with tests.
- **Permissions:** none.

## 3. Player groups ("Family", "Friends", …)

**Model** (in `models.py`):
```python
@dataclass
class Group:
    name: str
    player_ids: list[str]
    id: str = field(default_factory=_new_id)
```
- Groups store player **ids**, not names, so renaming a player keeps them in their groups.
- A group manager like `Roster` handles validation (unique names), and removing a player also removes them from every group.

**Choosing who plays:**
- Add `RoundSetup.select_only(ids)`. Because `RoundSetup` records who is *left out*, this becomes "leave out everyone who isn't in the group".
- On the home screen, a row of `ft.Chip`s above the player list: tap "Family" to tick just that group.

**Storage:**
- Bump `FORMAT_VERSION` to 2 in `storage.py` and add a `"groups"` list.
- `players_from_json` already ignores keys it doesn't know. The version-2 loader should treat version-1 data as "no groups".
- Add tests for loading version-1 data.

**Remembering the last round (optional):** save `RoundSetup` (mode and left-out ids) the same way, under its own key, e.g. `whose_turn.setup`.

## 4. Publishing

### Google Play (Android App Bundle)

**Signing key:** create one once, and keep it **and its passwords** somewhere safe. Losing it means you can't update the app.
```sh
keytool -genkey -v -keystore ~/keys/whose-turn-upload.jks \
  -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

**Non-secret settings** go in `pyproject.toml`:
```toml
[tool.flet.android.signing]
key_store = "/Users/you/keys/whose-turn-upload.jks"
key_alias = "upload"
```

**Passwords** go in environment variables, never in the repo:
`FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD`, `FLET_ANDROID_SIGNING_KEY_PASSWORD`.

**Build:**
- `uv run flet build aab -v`, then upload `build/aab/*.aab` in the Play Console.
- Google Play requires a higher `--build-number` (or `[tool.flet]` build number) for every upload. Bump `[project].version` for each release too.

**Play Console needs:**
- a developer account (one-off fee);
- a privacy policy URL. The app collects nothing, which makes that simple, but kids' apps go through the "Designed for Families" questions;
- screenshots;
- a 512×512 icon, which can be made from `src/assets/icon.png`.

**Adaptive icon (optional):** `[tool.flet.android] adaptive_icon_background = "#5E35B1"` makes the icon look right on every launcher shape.

### iOS (later)

**Needs:**
- a Mac with Xcode;
- CocoaPods;
- an Apple Developer account (yearly fee).

**Settings:**
- Set `[tool.flet.ios] team_id = "..."`, plus `export_method` and `provisioning_profile` as needed.
- Test first with `uv run flet build ios-simulator`, then build with `uv run flet build ipa`.

**Photo features:** iOS needs usage descriptions (e.g. `NSCameraUsageDescription`). The `permissions = ["camera", "photo_library"]` bundles add these, and wording can be customised with `[tool.flet.ios.info]`.

**Code changes:** nothing to change in the app code itself; storage and navigation already work on iOS.
