#!/usr/bin/env bash
# Rättar övningsbutiken i ditt repo med ett enda kommando. Klistra in i terminalen i din codespace:
#
#   curl -fsSL https://raw.githubusercontent.com/kaysismail-83/techretail-tests/main/scripts/fixa_butiken.sh | bash
#
# Vad det gör, i ordning:
# 1. Letar upp ditt repo techretail-tests.
# 2. Hämtar kursledarens rättade butik (version 2026.11.0) och byter ut den gamla.
# 3. Startar om butiken och sparar ändringen i en commit.
# 4. Skickar upp ändringen till GitHub (git push).
# Dina tester, din teststrategi och din AI-logg rörs inte. Du kan köra kommandot flera gånger.

set -u
MALL="${FIXA_MALL:-https://raw.githubusercontent.com/kaysismail-83/techretail-tests/main}"
URL="${TECHRETAIL_URL:-http://127.0.0.1:8000}"
export PATH="$HOME/.local/bin:$PATH"

rad() { echo; echo "==> $1"; }
stopp() {
    echo
    echo "------------------------------------------------------------"
    echo "STOPP. Det gick inte hela vägen: $1"
    echo "Inget av ditt eget arbete är borttaget."
    echo "Markera allt i terminalen, kopiera och klistra in det i tråden"
    echo "under inlägget om butiken i kanalen Allmänt i Teams."
    echo "------------------------------------------------------------"
    exit 1
}

rad "Steg 1 av 4: Letar upp ditt repo"
if [ -f Makefile ] && [ -f scripts/ikapp.py ]; then
    :
elif top=$(git rev-parse --show-toplevel 2>/dev/null) && [ -f "$top/scripts/ikapp.py" ]; then
    cd "$top"
else
    hittade=$(ls -d /workspaces/*/scripts/ikapp.py 2>/dev/null)
    if [ "$(printf '%s\n' "$hittade" | grep -c .)" = "1" ]; then
        cd "$(dirname "$(dirname "$hittade")")"
    else
        stopp "hittade inte repot. Öppna din codespace för techretail-tests och kör kommandot i terminalen där."
    fi
fi
echo "Repot: $(pwd)"
command -v uv >/dev/null 2>&1 || stopp "programmet uv saknas. Kör kommandot i din codespace, inte på egen dator."

rad "Steg 2 av 4: Hämtar den rättade butiken och byter ut den gamla"
mkdir -p scripts
curl -fsSL -o scripts/uppdatera_butiken.py "$MALL/scripts/uppdatera_butiken.py" \
    || stopp "kunde inte hämta rättelsen från GitHub. Vänta en minut och kör kommandot igen."
logg="${TMPDIR:-/tmp}/fixa_butiken.log"
if uv run --quiet python scripts/uppdatera_butiken.py >"$logg" 2>&1; then
    echo "Butiken är utbytt."
else
    cat "$logg"
    stopp "bytet av butiken misslyckades (steg 2)."
fi
FILER=()
for f in pyproject.toml uv.lock sut .devcontainer/post-create.sh scripts/uppdatera_butiken.py; do
    if [ -e "$f" ] || git ls-files --error-unmatch "$f" >/dev/null 2>&1; then FILER+=("$f"); fi
done
git add -A -- "${FILER[@]}"
if ! git diff --cached --quiet -- "${FILER[@]}"; then
    git commit -q -m "Patch: butiken 2026.11.0" -- "${FILER[@]}" || stopp "kunde inte spara ändringen i en commit (steg 2)."
fi

rad "Steg 3 av 4: Kontrollerar att butiken kör den nya versionen"
version() { curl -fsS --max-time 5 "$URL/health" 2>/dev/null | sed -n 's/.*"version":"\([^"]*\)".*/\1/p'; }
if [ -z "$(version)" ]; then
    uv run --quiet python scripts/shop.py start >/dev/null 2>&1
fi
v=$(version)
if [ "$v" != "2026.11.0" ]; then
    uv run --quiet python scripts/shop.py stop >/dev/null 2>&1
    uv run --quiet python scripts/shop.py start >/dev/null 2>&1
    v=$(version)
fi
[ "$v" = "2026.11.0" ] || stopp "butiken svarar inte med version 2026.11.0 (den svarar: ${v:-inget}). Starta om din codespace och kör kommandot igen."
echo "Butiken kör version $v."

rad "Steg 4 av 4: Skickar upp ändringen till GitHub"
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "Repot har ingen koppling till GitHub, så inget skickas upp."
    plats="sparad i repot"
elif git push -q origin HEAD 2>/dev/null; then
    echo "Uppskickat."
    plats="sparad på GitHub"
elif git pull -q --rebase --autostash origin "$(git branch --show-current)" >/dev/null 2>&1 && git push -q origin HEAD; then
    echo "Uppskickat (GitHub hade en nyare ändring, som nu är hämtad)."
    plats="sparad på GitHub"
else
    stopp "git push gick inte (steg 4). Butiken är ändå rättad i din codespace."
fi

echo
echo "============================================================"
echo "KLART! Butiken är rättad (version 2026.11.0) och $plats."
echo "Du behöver inte göra något mer."
echo "============================================================"
