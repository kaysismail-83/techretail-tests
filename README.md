# Mitt testrepo för TechRetail AB

Du är nyanställd i Anna Bergströms testteam på TechRetail AB. I dag testas allt för hand, och före varje release tar regressionstesterna flera dagar. Testerna du bygger fördelas på tre nivåer i testpyramiden: komponent (enhet), API och GUI. Den lägsta nivån kallas komponenttest (enhetstest). Under kursen bygger du upp automatiserade tester för företagets webbutik, en lektion i taget.

Det här repot är ditt. Du lägger till nya tester varje vecka, och i slutet av kursen är repot din inlämning.

Repot innehåller två saker:

- **Dina tester** i `tests/`, `pages/` och `src/`. Startkoden har `# TODO` där du ska skriva.
- **TechRetail-butiken**, systemet som du testar (system under test). Den ligger färdigpackad i `sut/` och startar automatiskt. Du behöver inte ändra något i den.

---

## Kom igång i GitHub Codespaces (rekommenderas)

Codespaces är en färdig utvecklingsmiljö i webbläsaren. Du behöver inte installera något på din dator, och det fungerar även på en låst arbetsdator. Allt du behöver är ett gratis GitHub-konto.

Räkna med 20–30 minuter första gången. Det mesta av tiden väntar du medan miljön byggs.

### Steg 1. Hämta startkoden

1. Ladda ner `techretail-tests.zip` från kursens kanal i Teams.
2. Packa upp zip-filen. Du får en mapp som heter `techretail-tests`.

**Förväntat resultat:** mappen innehåller bland annat `README.md`, `Makefile` och mapparna `tests`, `pages` och `sut`.

### Steg 2. Lägg upp repot på ditt GitHub-konto

1. Logga in på [github.com](https://github.com). Skapa ett gratiskonto om du inte har ett.
2. Klicka på **+** uppe till höger och välj **New repository**.
3. Ge repot namnet `techretail-tests`. Välj **Private**. Kryssa **inte** i "Add a README file".
4. Klicka på **Create repository**.
5. På sidan som visas, klicka på länken **uploading an existing file**.
6. Öppna mappen `techretail-tests` på din dator, markera **allt innehåll i mappen** och dra det till webbläsaren. Dra innehållet, inte själva mappen.
7. Skriv `Startkod` som commit-meddelande och klicka på **Commit changes**.

**Förväntat resultat:** repot på GitHub visar mapparna `.devcontainer`, `.github`, `tests`, `pages`, `sut` med flera.

> *Om det blir fel:* saknas `.devcontainer` eller `.github`? Mappar som börjar med punkt är dolda på Mac. Tryck **Cmd + Shift + punkt** i Finder så syns de, och dra sedan in dem också.

### Steg 3. Öppna repot i Codespaces

1. På repots sida på GitHub, klicka på den gröna knappen **Code**.
2. Välj fliken **Codespaces** och klicka på **Create codespace on main**.
3. Vänta tills byggstegen är klara. Första gången tar det 5–10 minuter.

**Förväntat resultat:** VS Code öppnas i webbläsaren, och terminalen längst ned skriver `Butiken är igång på http://127.0.0.1:8000`.

### Steg 4. Kontrollera miljön

Skriv i terminalen:

```bash
make doctor
```

**Förväntat resultat:** alla rader är `[OK]` eller `[INFO]`, och sista raden är `Allt ser bra ut. Du är redo för kursen.`

> *Om det blir fel:* varje `[FEL]` följs av en rad som säger vad du ska göra. Åtgärda uppifrån och ned och kör `make doctor` igen. Står det `git vet inte vem du är`? Kör de två `git config`-kommandona som visas, med ditt eget namn och din e-post.

### Steg 5. Titta på butiken

Öppna fliken **Ports** längst ned i VS Code och klicka på jordgloben vid port 8000. Butiken öppnas i en ny flik. Logga in med `kund@example.com` och lösenordet `Test1234!`.

API-dokumentationen finns på samma adress, med `/docs` på slutet.

### Spara kvoten

Ett gratiskonto har en månadskvot för Codespaces (120 kärntimmar, se [GitHub Docs](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)). Med två kärnor räcker den till ungefär 60 timmar per månad. Stäng din codespace när du är klar: **Code → Codespaces → … → Stop codespace**. Den stängs också automatiskt efter en stunds inaktivitet.

---

## Lokalt på din egen dator (valfritt)

Välj det här bara om du vill arbeta utan Codespaces. Du behöver rätt att installera program.

1. Installera [git](https://git-scm.com/downloads) och [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Packa upp zip-filen och öppna en terminal i mappen `techretail-tests`.
3. Installera paket och webbläsare:
   ```bash
   uv sync
   uv run playwright install chromium
   ```
4. Gör mappen till ett git-repo och koppla det till ditt GitHub-repo från steg 2 ovan (skapa repot utan att ladda upp filer):
   ```bash
   git init -b main
   git add .
   git commit -m "Startkod"
   git remote add origin https://github.com/<ditt-användarnamn>/techretail-tests.git
   git push -u origin main
   ```
5. Starta butiken och kontrollera miljön:
   ```bash
   make shop
   make doctor
   ```

**Windows utan `make`?** Kör kommandot direkt i stället:

| make | Samma sak utan make |
|---|---|
| `make shop` | `uv run python scripts/shop.py start` |
| `make doctor` | `uv run python scripts/doctor.py` |
| `make test` | `uv run pytest` |
| `make milstolpe L=1` | `uv run pytest -m milestone_l1 -v` |

---

## Så arbetar du varje vecka

```bash
make shop               # starta butiken (sker automatiskt i Codespaces)
make test               # kör alla dina tester
make milstolpe L=1      # kontrollera veckans milstolpe (byt 1 mot lektionens nummer)
git add .
git commit -m "Lektion 1: fem egna komponenttester"
git push
```

Skriv `make` för att se alla genvägar.

## Milstolpar – vad krävs varje vecka?

Varje lektion har en milstolpe. Den kontrolleras automatiskt med `make milstolpe L=<nummer>`. Grönt betyder att G-basen för lektionen är klar. Samma kontroller används när din inlämning bedöms.

| Lektion | Milstolpe (G-bas) | Filer |
|---|---|---|
| 1 | Minst 5 egna komponenttester för prisreglerna, alla gröna, och din första egna commit | `tests/unit/test_pricing.py` |
| 2 | `ProductPage` klar och minst 3 egna GUI-tester som använder den, alla gröna, utan fasta väntetider | `pages/product_page.py`, `tests/gui/test_produkt.py` |
| 3 | Grön pipeline med GUI-testerna i CI, en egen marker och en egen fixture, körtid mätt före och efter | `.github/workflows/ci.yml`, `docs/matningar.csv` |
| 4 | Minst 6 egna API-tester och ett test som bevisar IDOR, markerat `xfail` | `tests/api/` |
| 5 | Anonymiseringsskriptet klart, 3 AI-genererade tester granskade och loggade, scenarier från kraven | `anonymisering/`, `ai/AI-logg.md`, `docs/scenarier.md` |
| 6 | k6-test med prestandabudget och tolkning, k6 och ZAP i CI | `perf/k6/`, `.github/workflows/prestanda-sakerhet.yml` |
| 7 | Eriks kundvagnstest stabilt 20 av 20 gånger, 10 CI-fel klassade, felsökningsrapport | `felsokning/`, `docs/felsokning.md` |
| 8 | Ett nytt verktyg och ett nytt test i MCP-servern, AI-loggpost om Playwright MCP | `mcp_server/`, `tests/unit/test_mcp_server.py` |

Milstolparna är till för dig. De är inte betygsgrundande var för sig, men inlämningen bygger på dem.

## Startpaket – ny kod inför varje lektion

Före varje lektion lägger kursledaren ut ett **startpaket** i Teams, till exempel `startpaket-l3.zip`. Det innehåller bara nya filer. Inget av det du redan har skrivit ändras.

1. Ladda ner paketet och dra zip-filen till rotmappen i VS Code.
2. Kör i terminalen:
   ```bash
   make startpaket ZIP=startpaket-l3.zip
   git push
   ```

**Förväntat resultat:** `Klart. … nya filer från startpaket-l3:` följt av en lista över filerna.

## Så kommer du ikapp på 10 minuter

Har du missat en lektion eller fastnat? Efter varje lektion lägger kursledaren ut ett **ikapp-paket** i Teams, till exempel `ikapp-l2-start.zip`. Det innehåller koden som en klar lösning av alla tidigare lektioner.

1. Ladda ner paketet från Teams.
2. Dra zip-filen till rotmappen i VS Code (filträdet till vänster).
3. Kör i terminalen:
   ```bash
   make ikapp ZIP=ikapp-l2-start.zip
   uv sync
   make test
   git push
   ```

**Förväntat resultat:** `Klart. … filer från ikapp-l2-start är på plats.` och gröna tester.

Inget av ditt arbete försvinner. Skriptet sparar det först i en egen gren som heter `mitt-arbete-fore-…`. Ikapp-paketet ger dig koden, inte texterna: dina texter i `docs/` och `ai/`, din tolkning i `perf/k6/` och din klassning av CI-fel rörs inte. De skriver du själv.

## Vad finns var?

```
techretail-tests/
├── src/techretail/pricing.py   prisregler som du testar med komponenttester (lektion 1)
├── pages/                      Page Objects: base_page och login_page är givna, product_page skriver du (lektion 2)
├── tests/
│   ├── unit/                   komponenttester
│   ├── gui/                    GUI-tester med Playwright
│   ├── api/                    API-tester (lektion 4)
│   └── milestones/             milstolpekontrollerna – ändra inte här
├── api/client.py               API-klient (lektion 4)
├── anonymisering/              anonymiseringsskriptet (lektion 5)
├── perf/k6/                    lasttest med k6 (lektion 6)
├── felsokning/                 instabila tester och CI-feldataset (lektion 7)
├── mcp_server/                 din MCP-server (lektion 8)
├── evals/                      valbart: evalfall för en chattbot
├── conftest.py                 gemensamma fixtures: base_url, page, logged_in_user
├── testdata.py                 påhittade testkonton
├── ai/AI-logg.md               din AI-logg (GRANSKA-kortet)
├── docs/teststrategi.md        din teststrategi (fylls på under kursen)
├── .github/workflows/ci.yml    CI-pipelinen (lektion 3)
├── .devcontainer/              inställningar för Codespaces
├── scripts/                    hjälpskript bakom make-kommandona
└── sut/                        TechRetail-butiken, färdigpackad – ändra inte här
```

## Testkonton och fakta om butiken

Alla konton har lösenordet `Test1234!`. Namnen är påhittade.

| E-post | Namn | Bra för |
|---|---|---|
| `kund@example.com` | Kim Kund | Vanlig kund med ordrar. Används av fixturen `logged_in_user` |
| `kund2@example.com` | Robin Ring | En annan kund med ordrar |
| `ny@example.com` | Noa Ny | Ny kund utan ordrar |
| `last@example.com` | Lo Låst | Låst konto – inloggningen ska nekas |

- Rabattkoder: `TECH10` (10 %), `VINTER15` (15 %), `SOMMAR20` (har gått ut).
- Frakt: 49 kr under 500 kr, fri frakt från 500 kr.
- Alla knappar, fält och länkar har ett `data-test`-attribut. I testerna når du dem med `page.get_by_test_id("...")`.
- Återställ butikens data: `make shop-reset`.

## När något går fel

| Det här ser du | Gör så här |
|---|---|
| `TechRetail-butiken svarar inte på http://127.0.0.1:8000` | Kör `make shop`. Hjälper det inte, kör `make shop-logg` och läs de sista raderna. |
| `Executable doesn't exist` eller `playwright install` | Kör `uv run playwright install --with-deps chromium`. |
| `ModuleNotFoundError` | Kör `uv sync`. |
| Ett GUI-test fallerar och du förstår inte varför | Kör `uv run pytest tests/gui -v --tracing retain-on-failure`. Ladda ner `trace.zip` från mappen `test-results/` och öppna den på [trace.playwright.dev](https://trace.playwright.dev). |
| `make: command not found` (Windows lokalt) | Använd kommandona i tabellen under "Lokalt". |
| `git push` nekas | Kör `git pull --rebase` och sedan `git push` igen. |

Fastnar du ändå? Klistra in hela felutskriften och utskriften från `make doctor` i kursens hjälpkanal. Det går fel för nästan alla någon gång, och felutskriften är det bästa sättet att hitta orsaken.
