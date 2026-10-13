# The AgencyZoom proxy

One small program on a machine with an address of its own. The board's
Worker sends its AgencyZoom reads here instead of straight to
api.agencyzoom.com, and the proxy forwards them from that address.

**Why.** Every Cloudflare Worker in a region leaves through a few shared
outbound addresses, and AgencyZoom's firewall judges the address, not our
account. On October 1, 6, 7 and 12 it refused the Worker for the afternoon,
and on October 13 from the first request of the day, while the same login
worked from anywhere else. A proxy gives AgencyZoom one address that is
ours alone, and one address to allowlist.

**What it does.** Takes a request from the Worker (with the shared key),
forwards it to api.agencyzoom.com unchanged, and hands the answer back
exactly as it came, 403s and 429s included, so the Worker's own pacing and
pausing keep working. Nothing without the key, nothing outside `/v1/api/`,
GET and POST only, no bodies or tokens in its log. `proxy/server.js`, no
dependencies; `node --test proxy/server.test.mjs` is its test.

## Setting it up (about 20 minutes)

You need a small Linux server with its own public address. A $5-6 a month
VPS is plenty (Hetzner, DigitalOcean, Vultr, Linode: the smallest Ubuntu
box). The proxy handles under two requests a second at most.

1. **Make the server.** Ubuntu 24.04, the smallest size, any US region.
   Note its public IP address. Add a DNS record for it:
   `az-proxy.floresinsuranceagency.com  A  <that IP>` (wherever the
   domain's DNS lives). The Worker needs HTTPS, and a name is how the
   certificate gets issued.

2. **Install Node and Caddy** (Caddy is the HTTPS front; it gets and renews
   the certificate itself):

       sudo apt update && sudo apt install -y nodejs npm caddy

3. **Put the proxy on it.** Copy `proxy/server.js` to `/opt/pantheon/server.js`.
   Make a key: `openssl rand -hex 32` -- keep it, the Worker needs the same
   one. Write `/etc/pantheon/proxy.env`:

       PROXY_KEY=<the key>
       PORT=8787

   and `/etc/systemd/system/pantheon-az-proxy.service` (a copy is in
   `proxy/pantheon-az-proxy.service`), then:

       sudo systemctl daemon-reload
       sudo systemctl enable --now pantheon-az-proxy
       sudo journalctl -u pantheon-az-proxy -n 5     # "pantheon az proxy on :8787"

4. **Caddy in front.** `/etc/caddy/Caddyfile` (a copy is in `proxy/Caddyfile`):

       az-proxy.floresinsuranceagency.com {
           reverse_proxy 127.0.0.1:8787
       }

   then `sudo systemctl reload caddy`. Check from anywhere:

       curl -H "x-pantheon-key: <the key>" https://az-proxy.floresinsuranceagency.com/healthz

   It answers `{"ok":true,"upstream":"https://api.agencyzoom.com","egress":"<the server's address>"}`.
   That `egress` address is the one to give AgencyZoom.

5. **Point the Worker at it.** Cloudflare dashboard -> Workers & Pages ->
   flores-board -> Settings -> Variables and Secrets, two secrets:

       AZ_PROXY_URL   https://az-proxy.floresinsuranceagency.com
       AZ_PROXY_KEY   <the key>

   The next refresh goes through the proxy; the Worker's log
   (`worker-private/az_log/<day>.json`) records the host it used. Remove the
   two secrets to go back to calling AgencyZoom directly.

## Keeping it

- `sudo journalctl -u pantheon-az-proxy -f` watches the requests go by: one
  line each, method, path, status, milliseconds.
- `sudo apt upgrade` now and then; Caddy renews the certificate itself.
- If AgencyZoom ever refuses the proxy's address too, the log shows 403s
  with `server: cloudflare` the same way, and the address in `/healthz` is
  the one to send them.
