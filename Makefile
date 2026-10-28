# Genvägar för kursen. Skriv  make  för att se alla.
# Varje mål är bara ett kortare sätt att skriva kommandot som står bredvid.

UV ?= uv
L ?= 1
PROFIL ?=
ETIKETT ?=
ARGS ?=
URL ?= http://127.0.0.1:8000

# Så att python hittar src/techretail och repots moduler även utanför pytest.
export PYTHONPATH := $(CURDIR)/src:$(CURDIR)

# Kontroll att lektionens startpaket finns: $(call kraver,fil,lektion)
kraver = @test -e $(1) || { echo "Filen $(1) saknas. Lägg till startpaketet för lektion $(2): make startpaket ZIP=startpaket-l$(2).zip"; exit 1; }

.DEFAULT_GOAL := hjalp
.PHONY: hjalp setup doctor shop shop-stop shop-reset shop-status shop-logg test test-unit test-gui test-api milstolpe milstolpar startpaket ikapp matning k6 k6-rok anonymisera erik trafsakerhet mcp evals

hjalp: ## Visa alla genvägar
	@echo "Genvägar (kör med: make <namn>)"
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /|/' | awk -F'|' '{printf "  %-12s %s\n", $$1, $$2}'

setup: ## Installera paket och webbläsare (görs automatiskt i Codespaces)
	$(UV) sync
	$(UV) run playwright install chromium

doctor: ## Kontrollera att miljön är redo
	@command -v $(UV) >/dev/null 2>&1 || { echo "  [FEL]  uv hittas inte. Se README.md, avsnittet 'Lokalt'."; exit 1; }
	@$(UV) run --quiet python scripts/doctor.py

shop: ## Starta butiken i bakgrunden (http://127.0.0.1:8000). Valfritt: PROFIL=l7-buggvariant
	@$(UV) run --quiet python scripts/shop.py start $(if $(PROFIL),--profil $(PROFIL))

shop-stop: ## Stoppa butiken
	@$(UV) run --quiet python scripts/shop.py stop

shop-reset: ## Återställ butikens testdata
	@$(UV) run --quiet python scripts/shop.py reset

shop-status: ## Visa om butiken svarar
	@$(UV) run --quiet python scripts/shop.py status

shop-logg: ## Visa de senaste raderna i butikens logg
	@tail -n 40 .shop/shop.log 2>/dev/null || echo "Ingen logg ännu. Starta butiken med: make shop"

test: ## Kör alla tester (utom milstolpekontrollerna)
	$(UV) run pytest

test-unit: ## Kör komponenttesterna
	$(UV) run pytest tests/unit -v

test-gui: ## Kör GUI-testerna (butiken måste vara igång)
	$(UV) run pytest tests/gui -v

test-api: ## Kör API-testerna (lektion 4)
	$(UV) run pytest tests/api -v -rx

milstolpe: ## Kontrollera en milstolpe, till exempel: make milstolpe L=2
	$(UV) run pytest -m milestone_l$(L) -v --no-header

milstolpar: ## Kontrollera alla milstolpar
	$(UV) run pytest -m milestone -v --no-header

startpaket: ## Lägg till veckans startpaket (bara nya filer): make startpaket ZIP=startpaket-l3.zip
	$(UV) run --quiet python scripts/startpaket.py "$(ZIP)"

ikapp: ## Kom ikapp med ett paket från kursledaren: make ikapp ZIP=ikapp-l2-start.zip
	$(UV) run --quiet python scripts/ikapp.py "$(ZIP)"

matning: ## L3: mät körtiden: make matning ETIKETT=fore (valfritt ARGS="-m smoke")
	$(UV) run --quiet python scripts/matning.py "$(ETIKETT)" $(ARGS)

k6: ## L6: lasttest med k6 mot butiken, resultat i perf/k6/resultat.json
	$(call kraver,perf/k6/load.js,6)
	k6 run -e BASE_URL=$(URL) --summary-export perf/k6/resultat.json perf/k6/load.js

k6-rok: ## L6: kort röktest med k6 (samma som i CI)
	$(call kraver,perf/k6/load.js,6)
	k6 run -e BASE_URL=$(URL) -e PROFIL=rok perf/k6/load.js

anonymisera: ## L5: kör anonymiseringsskriptet på den syntetiska exporten
	$(call kraver,anonymisering/anonymize.py,5)
	$(UV) run python -m anonymisering.anonymize anonymisering/data/kundexport_syntetisk.csv anonymisering/ut/kundexport_anonymiserad.csv

erik: ## L7: kör Eriks kundvagnstest 20 gånger
	$(call kraver,felsokning/instabila,7)
	$(UV) run pytest felsokning/instabila --count 20 -q

trafsakerhet: ## L7: räkna träffsäkerheten för din klassning
	$(call kraver,felsokning/trafsakerhet.py,7)
	$(UV) run python felsokning/trafsakerhet.py

mcp: ## L8: lista verktygen i din MCP-server
	$(call kraver,mcp_server/server.py,8)
	$(UV) run python -m mcp_server.server --lista

evals: ## Valbart: kör evalfallen för chattbotten
	$(call kraver,evals,8)
	$(UV) run pytest evals -v
