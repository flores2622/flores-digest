#!/bin/bash
# Pantheon's AgencyZoom proxy -- one-shot install on a fresh Ubuntu 24.04 box
# in a US data center (proxy/README.md says why). Run as root:
#
#   curl -fsSL https://raw.githubusercontent.com/flores2622/flores-digest/main/proxy/install.sh | bash
#
# It installs Node and Caddy, downloads proxy/server.js, the systemd unit and
# the Caddyfile from this repository, makes the shared key ON THE SERVER (it is
# never typed or sent anywhere), starts everything and prints the two secrets
# the Worker needs. Safe to run again: the key is kept, the files refreshed.
set -euo pipefail
RAW="${PANTHEON_RAW:-https://raw.githubusercontent.com/flores2622/flores-digest/main/proxy}"

[ "$(id -u)" = 0 ] || { echo "run as root"; exit 1; }
echo "== installing node, caddy"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nodejs caddy curl openssl >/dev/null
mkdir -p /opt/pantheon /etc/pantheon /etc/caddy

echo "== downloading the proxy from $RAW"
curl -fsSL "$RAW/server.js" -o /opt/pantheon/server.js
curl -fsSL "$RAW/pantheon-az-proxy.service" -o /etc/systemd/system/pantheon-az-proxy.service
curl -fsSL "$RAW/Caddyfile" -o /etc/caddy/Caddyfile
node --check /opt/pantheon/server.js

if [ ! -s /etc/pantheon/proxy.env ]; then
  echo "== making the shared key"
  KEY=$(openssl rand -hex 32)
  printf 'PROXY_KEY=%s\nPORT=8787\n' "$KEY" > /etc/pantheon/proxy.env
fi
chmod 600 /etc/pantheon/proxy.env
# systemd reads the file as root, then drops to the service's user
KEY=$(sed -n 's/^PROXY_KEY=//p' /etc/pantheon/proxy.env)

echo "== starting"
systemctl daemon-reload
systemctl enable --now pantheon-az-proxy >/dev/null
systemctl restart pantheon-az-proxy
systemctl enable --now caddy >/dev/null
systemctl reload caddy || systemctl restart caddy
sleep 2
echo "== the proxy says:"
curl -s -H "x-pantheon-key: $KEY" http://127.0.0.1:8787/healthz \
  || echo "(no answer -- run: journalctl -u pantheon-az-proxy -n 20)"
echo
echo
echo "=================================================================="
echo " DONE. Copy these two into Cloudflare: Workers & Pages ->"
echo " flores-board -> Settings -> Variables and Secrets (type Secret):"
echo
echo "   AZ_PROXY_URL   https://az-proxy.floresinsuranceagency.com"
echo "   AZ_PROXY_KEY   $KEY"
echo
echo " The 'egress' address above is the one to give AgencyZoom."
echo " Caddy gets the HTTPS certificate on its own once the DNS record"
echo " az-proxy.floresinsuranceagency.com -> this server's IP exists."
echo "=================================================================="
