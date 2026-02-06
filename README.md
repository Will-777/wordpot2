# Wordpot2

A WordPress honeypot that detects probes for plugins, themes, timthumb and other common files used to fingerprint a WordPress installation.
Wordpot2 mimics a **WordPress 6.4.3** site using the **Twenty Twenty-Four** theme (default). It logs all probing attempts including login bruteforce, plugin/theme enumeration, and author discovery.
Originally forked from [Wordpot by Brindisi](https://github.com/gbrindisi/wordpot) (Python 2 / Flask 0.x), fully rewritten for **Python 3.10+ / Flask 3.x**.

## Quick Start

```bash
pip install -r requirements.txt
python wordpot2.py --host=127.0.0.1 --port=5000
```

Then visit `http://127.0.0.1:5000` — you should see a WordPress-looking site.

## Configuration

Edit `wordpot.conf` or use command line arguments:

```bash
python wordpot2.py --help
```

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host address | `127.0.0.1` |
| `--port` | Port number | `80` |
| `--title` | Blog title | `Here the Title` |
| `--theme` | Theme name | `twentytwentyfour` |
| `--plugins` | Fake plugins (comma-separated) | all allowed |
| `--themes` | Fake themes (comma-separated) | all allowed |
| `--ver` | WordPress version to mimic | `6.4.3` |
| `--server` | Custom Server header | `Apache/2.4.57 (Ubuntu)` |

## What gets logged

All activity is logged to `logs/wordpot.log`:

- Login attempts (username + password captured)
- Admin panel probes
- Plugin and theme enumeration
- Author discovery (`?author=N`)
- Common file probes (readme.html, xmlrpc.php)
- TimThumb/Uploadify probes

Optional: enable [hpfeeds](https://hpfeeds.org/) in `wordpot.conf` to forward JSON logs to a centralized collector.

## Theme support

Themes go in `wordpot/static/wp-content/themes/`. Each theme needs a matching HTML template in `wordpot/templates/` (e.g. `twentytwentyfour.html`).

Available themes:
- `twentytwentyfour` — WordPress 6.4 default (recommended)
- `twentyeleven` — Legacy theme (in `templates/v2.8/`)

Templates use the [Jinja2](https://jinja.palletsprojects.com/) template engine.

## Plugins (beta)

Wordpot2 is expandable with plugins to simulate specific WordPress vulnerabilities.

Built-in plugins:
- **badlogin** — Captures login credentials
- **commonfiles** — Serves readme.html, xmlrpc.php
- **userenumeration** — Responds to `?author=N` probes
- **timthumb** — Detects TimThumb/Uploadify probes

See the [wiki](https://github.com/gbrindisi/wordpot/wiki/Plugins) for writing custom plugins.

## Docker deployment

For Docker/production deployment with Nginx and WPScan testing, see [ITSupportAsia](https://github.com/Will-777/ITSupportAsia) (private repo).

## WPScan results

Tested with WPScan 3.8.28 — the honeypot is successfully identified as:
- ✅ WordPress 6.4.3 (via Meta Generator + readme.html)
- ✅ Theme: Twenty Twenty-Four
- ✅ User enumeration working

## Links

- Original project: [Wordpot by Brindisi](https://github.com/gbrindisi/wordpot)

## License

ISC License.

> Copyright (c) 2012, Gianluca Brindisi < g@brindi.si >
>
> Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
>
> THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
