# Wordpot2

A WordPress honeypot that detects probes for plugins, themes, timthumb and other common files used to fingerprint a WordPress installation.

Wordpot2 mimics a **WordPress 6.4.3** site using the **Twenty Twenty-Four** theme (default). It logs all probing attempts including login bruteforce, plugin/theme enumeration, and author discovery.

Originally forked from [Wordpot by Brindisi](https://github.com/gbrindisi/wordpot) (Python 2 / Flask 0.x), fully rewritten for **Python 3.10+ / Flask 3.x**.

## Quick Start

```bash
pip install -r requirements.txt
python wordpot2.py --host=127.0.0.1 --port=5000
```

Then visit `http://127.0.0.1:5000` -- you should see a WordPress-looking site.

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

Themes live in `wordpot/static/wp-content/themes/`. Each theme needs a matching HTML template in `wordpot/templates/` named after the theme (e.g. `twentytwentyfour.html`).

Available themes:
- `twentytwentyfour` -- WordPress 6.4 default (recommended)
- `twentyeleven` -- Legacy theme (in `templates/v2.8/`)

Note: Flask serves static files with `static_url_path=''` so assets are served under `/wp-content/` (not `/static/wp-content/`) just like a real WordPress site.

Templates use the [Jinja2](https://jinja.palletsprojects.com/) template engine.

## Plugins (beta)

Wordpot2 is expandable with plugins to simulate specific WordPress vulnerabilities.

Built-in plugins:
- **badlogin** -- Captures login credentials
- **commonfiles** -- Serves readme.html, xmlrpc.php
- **userenumeration** -- Responds to `?author=N` probes
- **timthumb** -- Detects TimThumb/Uploadify probes

See the [wiki](https://github.com/gbrindisi/wordpot/wiki/Plugins) for writing custom plugins.

## WPScan validation

Tested with WPScan 3.8.28:
- [x] WordPress 6.4.3 detected (via Meta Generator + readme.html)
- [x] Theme Twenty Twenty-Four identified
- [x] User enumeration working
- [x] Proper `/wp-content/` paths (no `/static/` leak)
- [ ] Plugin fingerprints not yet detectable
- [ ] User enumeration needs WordPress-style `/author/` redirects

## Docker deployment

Wordpot2 runs standalone with `python wordpot2.py`, but for production you'll want gunicorn behind a reverse proxy. Here's how:

### Dockerfile example

```dockerfile
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Important: suppress gunicorn's Server header so Flask can spoof Apache
RUN printf 'import gunicorn.http.wsgi\n\
_orig = gunicorn.http.wsgi.Response.default_headers\n\
def _no_server(self):\n\
    return [h for h in _orig(self) if not h.lower().startswith("server:")]\n\
gunicorn.http.wsgi.Response.default_headers = _no_server\n' > /opt/gunicorn.conf.py

COPY . .
EXPOSE 8000
CMD ["gunicorn", "wordpot2:app", "-c", "/opt/gunicorn.conf.py", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### Key tips for realism

- **Server header**: gunicorn overrides Flask's spoofed `Server` header by default. The config above fixes that so `wordpot.conf`'s `SERVER` value is used instead.
- **Reverse proxy**: put Nginx in front to add realistic logging and block suspicious paths (`.git`, `.env`, etc.).
- **Test with WPScan**: always validate your setup with `wpscan --url http://your-honeypot --enumerate u,vp,vt` to check what leaks.

## Links

- Original project: [Wordpot by Brindisi](https://github.com/gbrindisi/wordpot)

## License

ISC License.

> Copyright (c) 2012, Gianluca Brindisi < g@brindi.si >
>
> Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
>
> THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.