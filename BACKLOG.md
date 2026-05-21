# Backlog

## Index

| # | Item | Section |
|---|---|---|
| 1 | Add `language` table with trigger | [Region & Language system → Migration tasks](#region--language-system) |
| 2 | Add `region` table with trigger | [Region & Language system → Migration tasks](#region--language-system) |
| 3 | Add `region_language` junction table with trigger | [Region & Language system → Migration tasks](#region--language-system) |
| 4 | Add nullable `language_fk` column to `naip` | [Region & Language system → Migration tasks](#region--language-system) |
| 5 | Seed languages, regions, and `region_language` rows | [Region & Language system → Migration tasks](#region--language-system) |

---

## Region & Language system

### Background

Certain Naips (physical prints) carry their text in a specific language. Tournament regions define which languages are permitted for competitive play. A Naip is legal in a region if and only if its language is in that region's allowlist.

### New tables

#### `language` (lookup)
| column | type | notes |
|---|---|---|
| id | INTEGER PK | |
| created_ts | TEXT | server default |
| updated_ts | TEXT | server default + trigger |
| code | TEXT UNIQUE NOT NULL | BCP-47 language tag e.g. `ja`, `en`, `zh-Hans` |
| name | TEXT NOT NULL | human-readable e.g. "Japanese" |
| desc | TEXT | optional notes |
| image_fk | INTEGER FK → image.id | flag image |

#### `region` (lookup)
| column | type | notes |
|---|---|---|
| id | INTEGER PK | |
| created_ts | TEXT | server default |
| updated_ts | TEXT | server default + trigger |
| code | TEXT UNIQUE NOT NULL | UN M.49 numeric code e.g. `392` (Japan), `150` (Europe), `019` (Americas) |
| name | TEXT NOT NULL | e.g. "Japan", "English-language regions" |
| desc | TEXT | optional notes |

#### `region_language` (junction — many-to-many)
Maps which languages are permitted in each region.

| column | type | notes |
|---|---|---|
| id | INTEGER PK | |
| created_ts | TEXT | server default |
| updated_ts | TEXT | server default + trigger |
| region_fk | INTEGER FK → region.id NOT NULL | |
| language_fk | INTEGER FK → language.id NOT NULL | |
| UNIQUE (region_fk, language_fk) | | |

### Naip change

Add `language_fk` to `Naip` (nullable FK → `language.id`). NULL means the language is unknown or not yet assigned.

### Legality query

A Naip is legal in a given region when:

```sql
EXISTS (
  SELECT 1
  FROM   region_language rl
  WHERE  rl.region_fk   = :region_id
    AND  rl.language_fk = naip.language_fk
)
```

### Design notes

- Language lives on `Naip`, not `Set`, because the same card number can appear in both a JP and an EN print within the same set (e.g. international promo sets).
- Region legality is derived — there is no `naip_region` junction. The region allowlist on `language` is the single source of truth. If a future requirement needs per-naip regional overrides, a `naip_region_override` table can be added later.
- `region_language` uses the same `updated_ts` trigger pattern as all other tables.
- `language.code` follows BCP-47 (stored as TEXT). `region.code` follows UN M.49 (stored as TEXT, zero-padded 3-digit string e.g. `"003"` not `3`) — covers both individual countries and macro-regions natively, eliminating the need for custom strings.

### Seed data

#### Languages (BCP-47)
| code | name |
|---|---|
| `ja` | Japanese |
| `en` | English |
| `fr` | French |
| `zh-Hans` | Simplified Chinese |
| `ko` | Korean |

Source: [Rules for the use of Different Languages](https://en.onepiece-cardgame.com/rules/announcements/lang_card_rule.php)

#### Regions (UN M.49)
| code | name | permitted languages |
|---|---|---|
| `392` | Japan | `ja` |
| `003` | North America | `en` |
| `150` | Europe | `en`, `fr` |
| `419` | Latin America and the Caribbean | `en` |
| `009` | Oceania | `en` |
| `145` | Western Asia (Middle East) | `en` |
| `156` | China (Mainland) | `zh-Hans` |
| `410` | Korea (Republic of) | `ko` |
| `702` | Singapore | `en`, `ja` |
| `458` | Malaysia | `en`, `ja` |
| `360` | Indonesia | `en`, `ja` |
| `608` | Philippines | `en`, `ja` |
| `158` | Taiwan | `ja`, `en` |
| `764` | Thailand | `ja`, `en` |
| `344` | Hong Kong S.A.R. | `ja`, `en` |

Source: [Global Entrance](https://www.onepiece-cardgame.com/global/) · [Language rules](https://en.onepiece-cardgame.com/rules/announcements/lang_card_rule.php)

> Note: Taiwan and Thailand allow both `ja` and `en` effective 2025-11-28. Europe allows both `en` and `fr` effective 2025-02-07.

### Migration tasks

1. Add `language` table with trigger.
2. Add `region` table with trigger.
3. Add `region_language` junction table with trigger.
4. Add nullable `language_fk` column to `naip` (no trigger needed — `naip` trigger already exists).
5. Seed languages, regions, and `region_language` rows per the tables above.

<!-- item numbers 1–5 match the Backlog Index above -->
