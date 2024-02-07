# degeneranki
Anki gacha pull add-on for a bit of extra dopamine. Currently supports "rolling" for Genshin Impact characters, with other franchises planned.

**NOTE:** This addon is only availabile for Anki 23.12.1+. For whatever reason, some older versions do not work and I do not have the time right now to try on multiple old versions. Support may come in the future.

## Installation
### AnkiWeb
You can install the add-on using [AnkiWeb](https://ankiweb.net/shared/info/651549367).

### Manual Installation (Not Recommended)
This is only if you want the latest version of degeneranki, which may not be fully tested.

1. Download this git repository.
2. Move the `src/degeneranki` directory into your addons directory.

## Usage
## Account Creation
You are unable to use this addon without creating an account.

To create an account:
1. Enter a valid "email"
2. Enter a secure password of at least 8 characters with at least 1 lowercase letter, uppercase letter, number, and symbol
3. Click "Sign Up"

## Account Deletion
Accounts deletion can be requested by emailing me at [me@omn0mn0m.com](mailto:me@omn0mn0m.com).

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
Roll probabilities are roughly based off of Genshin Impact's roll system, which is described in detail [here](https://www.hoyolab.com/article/497840).

##### Base Probabilities
| Rarity | Probability (%) |
|--------|-----------------|
| 3      | 94.3            |
| 4      | 5.1             |
| 5      | 0.6             |

##### Soft Pity Probabilities
###### 4-Star
Starting at 8 pity, the chance of obtaining a 4-star roll is 100% however 5-star rolls will take precedence.

###### 5-Star
Starting at 73 pity, the chance of obtaining a 5-star roll is 0.7% then increases by 7% every unsuccessful roll until reaching 100% at 90 pity.

##### Hard Pity
You are guaranteed a 4-star character or weapon every 10 rolls without a 4-star.

You are guaranteed a 5-star character every 90 rolls without a 5-star.

### Viewing Inventory
Click the "Characters" tab.

TODO: New rolls show up as larger images than your existing inventory when you first open Anki. This will be fixed in a future update.

## Build
Running `make all` will create a `.ankiaddon` file in the `buld` directory.

## Contributing
Contributions are welcome :). Please submit contributions as pull requests. A pull request template is available automatically when creating pull requests or can be found [here](https://github.com/omn0mn0m/degeneranki/blob/main/.github/PULL_REQUEST_TEMPLATE.md).
