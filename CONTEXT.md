# tinyinternet.company

One-page twilight cabin scene.

## Glossary

**Scene**:
The full-bleed page. A background painting carries the emblem, the wordmark, the contact pill, and the values sign.
_Avoid_: hero as a separate product

**Emblem**:
The mountain, wave, and hibiscus mark. One vector drawing, `logo/mark-desktop.svg`.
_Avoid_: logo, when that would also mean the lockup

**Wordmark**:
The centered name and tagline, set in HTML.
_Avoid_: title image

**Contact pill**:
The email control, set in HTML.
_Avoid_: button image

**Values sign**:
The garden sign. Its frame is painted. Its four lines are HTML.
_Avoid_: poster, card

**Scene assets**:
The module that maps each part of the scene to the file that paints it. Callers name the part. The map is the custom properties at the top of `starter/styles.css`.
_Avoid_: manifest, asset pipeline

**Values frame**:
The painted posts, flowers, lantern, and blank planks behind the values lines. Derived from the painted master by `ui/build_values_frame.py`.
_Avoid_: the sign copy

## Relationships

- The scene places the emblem, the wordmark, the contact pill, and the values sign.
- Scene assets chooses the file for the background, the emblem, and the values frame.
- The values sign reads its lines from HTML and its frame from scene assets.
- The lockup composes the emblem. It does not redraw it.
