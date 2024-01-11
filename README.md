# degeneranki
Anki gacha pull add-on for a bit of extra dopamine.

**NOTE:** This addon is only availabile for Anki 23.12.1+. For whatever reason, some older versions do not work and I do not have the time right now to try on multiple old versions. Support may come in the future.

## Installation
### AnkiWeb
You can install the add-on using [AnkiWeb](https://ankiweb.net/shared/info/651549367).

### Manual Installation (Not Recommended)
This is only if you want the latest version of degeneranki, which may not be fully tested.

1. Download this git repository.
2. Move the `src/degeneranki` directory into your addons directory.

## Usage
### Gacha Points
Gacha points are the currency used to roll for characters/ weapons. They are earned automatically when you answer a card as "Good" or "Easy".

You can check your gacha points under "Tools" > "degeneranki".

### Rolling
Rolling is how you obtain collectables. There is a chance of getting either a weapon (does nothing) or a character (also does nothing, but people want these(?)).

#### How to Roll
1. Go to "Tools" > "degeneranki".
2. Roll by hitting the "Roll" button.

#### Rarities
- Weapons are either 3-star or 4-star rarity.
  - 5-star weapons may eventually be added, depending if people want them.
- Characters are either 4-star or 5-star rarity.
- degeneranki uses a "pity" system to guarantee an occasional good roll.
  - You are guaranteed a 4-star weapon or character every 10 rolls without a 4-star roll.
  - You are guaranteed a 5-star character every 90 rolls without a 5-star roll.
  - Soft Pity: After 75 rolls without a 5-star, your probability of obtaining a 5-star increases.

A breakdown of roll probabilities are in the next section.

#### Roll Probabilties
This are very much subject to change.

##### Base Probabilities
| Rarity | Probability (%) |
|--------|-----------------|
| 3      | 94.53           |
| 4      | 4.975           |
| 5      | 0.4975          |

##### Soft Pity Probabilities
| Rarity | Probability (%) |
|--------|-----------------|
| 3      | 85.48           |
| 4      | 12.90           |
| 5      | 1.613           |

### Viewing Collection
This is not yet implemented...

## Build
Currently, only manually creating the `.ankiaddon` file works.

1. Zip the contents of `src/degeneranki`
   - Ignore `user_files/data.json` and `user_files/database.db`
   - Ignore `__pycache__`
2. Rename `.zip` to `.ankiaddon`

## Contributing
Contributions are welcome :). Please submit contributions as pull requests. A pull request template is available automatically when creating pull requests or can be found [here](https://github.com/omn0mn0m/degeneranki/blob/main/.github/PULL_REQUEST_TEMPLATE.md).
