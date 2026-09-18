# Netopier v2 — návrh projektu a úloha Martin Sliz

Aktualizované: 11. septembra 2026. Stav: projekt [Netopier](https://linear.app/xvadur/project/netopier-5ad533669129/overview) a úloha [XDR-142](https://linear.app/xvadur/issue/XDR-142/rozobrat-30-prispevkov-martina-sliza-data-analyticke-postupy-grafy-a) sú vytvorené a spätne overené v Lineare. Výskum 30 príspevkov zatiaľ nie je dokončený.

## Projekt Netopier

Zachovať existujúci v2 základ a rozvinúť verejné spravodajstvo, výskum a dátové vysvetľovanie. Linear bude evidovať výsledky, závislosti a overenie práce. Zdrojové dáta a implementácia zostávajú v Netopieri.

Aktuálna mapa pracovných oblastí; okrem explicitnej Slizovej úlohy ide o návrh rozdelenia budúcej práce, nie o spustenú implementáciu:

| Oblasť | Existujúci základ | Nasledujúci výsledok |
| --- | --- | --- |
| Backend v2 | MinifluxGateway, ArticleArchive, StoryEngine, FeedProjector; historické integračné dôkazy | Zmapovať aktuálne kontrakty a po rozhodnutí o runtime znovu overiť obmedzený RSS → archív → udalosť → API priechod. |
| Frontend Vydanie | Schválená obrazová referencia, DESIGN.md, HTML, ukážkové dáta a assety | Dokončiť vybraný frontend, overiť desktop/mobil a pripojiť reálne projekcie backendu. |
| Zdroje | Discovery a register verejných inštitucionálnych zdrojov | Pri konkrétnych zdrojoch overiť získateľnosť, polia, históriu, aktualizácie a pôvod. |
| Research lane | Existujúce výskumné dokumenty a vzorky verejných zdrojov | Definovať a overiť cestu otázka → zdroje → dôkazy → analýza → kontrolovaný výstup. Sliz patrí sem. |
| Orchestrácia cez OpenClaw | Používateľom požadovaný smer; žiadne zapnutie v tejto práci | Navrhnúť lacný model na prideľovanie a sledovanie práce, rozpočty, retry limity, eskaláciu a prevádzkový dôkaz. Konkrétny model vybrať podľa aktuálnej ceny a malej skúšky. |
| Grafy a Remotion | Zatiaľ nenájdený implementovaný renderovací reťazec | Z overených dát a analytických postupov odvodiť grafické zadania a 2–3 funkčné motion ukážky. |
| Redakčná kontrola a publikácia | Produktová hypotéza, proveniencia a ľudská zodpovednosť | Prepojiť návrh výstupu, kontrolu dôkazov, schválenie a históriu verzií. |

OpenClaw má koordinovať výskumnú prácu nad rozhraniami Netopiera. Nemá nahradiť vlastníctvo pollingu v Minifluxe ani ukladať autoritatívne dáta namiesto backendu. Lacný model môže vyberať ďalší krok a kontrolovať stav; náročná analýza má mať jasnú eskaláciu. Aktivácia runtime, trvalá prevádzka a modelový rozpočet zostávajú samostatným vykonaním.

## Úloha v Lineare — XDR-142

**Projekt:** [Netopier](https://linear.app/xvadur/project/netopier-5ad533669129/overview), tím Xvadur. Úloha XDR-142 je v stave Backlog, bez priradeného riešiteľa.

**Názov:** Rozobrať 30 príspevkov Martina Sliza: dáta, analytické postupy, grafy a publikačný rytmus

**Oblasť:** Research lane / dátová analytika.

**Cieľ:** Z verejnej práce dátového novinára Martina Sliza zistiť, aké zdroje sleduje, aké otázky nad nimi rieši, čo s dátami robí, ako volí grafy a kedy publikuje. Výsledkom budú použiteľné analytické postupy a podklady pre vlastné výstupy Netopiera.

**Zdroj:** https://www.instagram.com/sliz.martin/ a priamo súvisiace autorské články či pôvodné dátové zdroje.

### Rozsah

1. Vybrať presne 30 dátových príspevkov naprieč témami a časom. Zachovať niekoľko opakovaní jednej série na porovnanie rutiny. Uviesť výberové pravidlo, dátum výberu a zdôvodnenie zahrnutia. Odlíšiť vlastné, spoluautorské a prevzaté príspevky.
2. Každý carousel prejsť celý vrátane popisu, poznámok pod grafmi a zdrojov. Zaznamenať poradie snímok. Pri videu zaradiť iba spracovateľný záznam s prepisom a časovými lokátormi; inak uviesť hranicu prístupu.
3. Pri všetkých 30 dohľadať čo najpresnejší pôvod dát, formát a overiť dostupnosť vstupov. Nezamieňať uvedený názov inštitúcie s nájdeným konkrétnym datasetom.
4. Oddeliť autorov publikovaný výrok, pozorovateľnú operáciu nad dátami, našu rekonštrukciu metódy a neoverenú hypotézu.
5. Preskúmať časovanie: dátum vydania dát, obdobie dát, dátum príspevku, prípadná aktualizácia článku, spúšťacia udalosť a opakovanie série. Oneskorenie rátať iba pri overených časoch. Tematicky vybraná vzorka 30 nie je úplný kalendár účtu; celkovú frekvenciu neodvodzovať bez úplného pokrytia definovaného obdobia.
6. Vybrať tri prípady s dostupnými vstupmi a nezávisle zopakovať výpočet alebo porovnanie; zaznamenať zhodu, odchýlku a príčinu.
7. Odvodiť opakovateľné postupy pre Netopier a 2–3 zadania pre Remotion. Funkčné motion ukážky sú dohodnutý nadväzujúci výstup, závislý od výberu a overenia dát; nie podmienka samotného čítania 30 príspevkov.

### Jeden záznam príspevku

- ID, URL, autorstvo, čas publikovania a získania, formát, séria, téma.
- Snímky s poradím a lokátormi tvrdení, grafov a citovaných zdrojov.
- Výskumná otázka a hlavný publikovaný záver.
- Zdroj/inštitúcia, konkrétny dataset alebo dokument, URL, vydanie, dátové obdobie, jednotky, populácia a menovateľ.
- Získanie vstupu a jeho stav: uvedený zdroj / nájdený dataset / získaná vzorka / reprodukovaný výpočet.
- Analytické operácie: filtrovanie, zoskupovanie, prepočet, normalizácia, váženie, časové porovnanie, spájanie zdrojov, vlastná metrika.
- Typ grafu, mapovanie hodnôt na os/veľkosť/farbu, mierka, baseline, zvýraznenie, neistota a možné zavádzajúce prvky.
- Funkcia každej snímky: otázka, prehľad, porovnanie, detail, dôsledok, metodická hranica alebo výzva čitateľovi.
- Časovanie a doložený spúšťač publikácie; neznámy spúšťač zostáva neznámy.
- Použiteľnosť pre Netopier: potrebné vstupy, aktualizovateľnosť, náročnosť, overenie a návrh statického/motion výstupu.

### Výstupy a akceptácia

- Jeden použiteľný dataset s presne 30 unikátnymi príspevkami a úplným pokrytím ich carouselov; explicitné medzery zostávajú označené.
- Register zdrojov previazaný na príspevky a reálne otázky, nie iba zoznam domén.
- Porovnanie analytických operácií, typov grafov a vysvetľovania naprieč snímkami.
- Rozbor publikačného časovania s presnou hranicou vzorky.
- Tri doložené reprodukcie a konkrétne návrhy použitia v Netopieri.
- 2–3 nadväzujúce Remotion zadania s dátovým vstupom, scénami, vysvetľovanou otázkou a overovacím kritériom; následne funkčné ukážky.
- Surové verejné podklady, URL, časy a hashe oddelené od interpretácie. Dáta v existujúcej konvencii `data/research/`, syntéza v `docs/research/`.

### Východisková vzorka, nie dokončenie úlohy

V tejto konverzácii boli predbežne čítané štyri príspevky:

- https://www.instagram.com/p/DcJIg9CCPIg/ — vládne cesty, uznesenia a diplomatické dni.
- https://www.instagram.com/p/DdGNzT5jkpQ/ — FinStat, tržby a sídla firiem podľa krajov.
- https://www.instagram.com/p/DdGz2sfDqpa/ — volebný barometer, jednotlivé meranie a model.
- https://www.instagram.com/p/DdHJX2OIC4_/ — porovnanie NMS a Focusu.

Tieto pozorovania zatiaľ nemajú kompletný uložený výskumný balík podľa vyššie uvedenej akceptácie. Úloha 30 príspevkov preto zostáva nesplnená.

## Prenos výskumu Eden / Instagram / Meta Ads / Patriksystems — 11. 9. 2026

Na explicitné zadanie uložiť zistenia a dokumenty z Codex tasku **Preskúmaj Eden integrácie** (ID `01a09175-3c74-7bf3-94cc-6873fc8ecf40`) vznikla v existujúcom projekte Netopier úloha [XDR-195 — Uložiť výskum: Eden, Instagram, Meta Ads a Patriksystems / COR-X](https://linear.app/xvadur/issue/XDR-195/ulozit-vyskum-eden-instagram-meta-ads-a-patriksystems-cor-x).

- [Eden, Instagram a Meta Ads — zistenia, možnosti a otvorené overenie](https://linear.app/xvadur/document/eden-instagram-a-meta-ads-zistenia-moznosti-a-otvorene-overenie-11-9-4d17b694b22d): syntéza celého rozhovoru, dokumentované integrácie, Saved/reposty, nároky na spracovanie médií, možnosti Meta prieskumu a otvorené hranice.
- [Patriksystems / COR-X — úplný prieskum a 20 Meta reklám](https://linear.app/xvadur/document/patriksystems-cor-x-uplny-prieskum-a-20-meta-reklam-11-9-2026-6dee56d5687b): celý obsah lokálneho [výskumného dokumentu](research/PATRIKSYSTEMS_WEB_SOURCES_2026-09-11.md), s dátumami v tabuľkách prevedenými na ISO formát kvôli správnemu importu do editora.
- Pri úlohe je nahraný aj nezmenený pôvodný Markdown: 16 465 bajtov, SHA-256 `6c457591b9f105d28eb1bfad45dea3352377aa0db6a98d8247c85f51b73cd3be`.

Overenie: oba dokumenty načítané späť cez konektor, skontrolované všetky sekcie, 20 reklamných ID a koniec dokumentu. Príloha stiahnutá späť; veľkosť aj SHA-256 zhodné s lokálnym originálom. Úloha prenosu má stav **Done**. Pripojenie Eden/Readwise, hromadný import Instagramu, plné spracovanie Reels a navrhnutý pilot 2 Reely + 2 carousely zostávajú nevykonané. Výskumné závery sú datované k overeniu v pôvodnom tasku; prenos ich nemení na nový runtime test. Raw konverzácia ostáva v Codexe.

Aktuálny zápis aj čítanie cez Linear konektor v tejto práci fungovali; historické zlyhanie uvedené nižšie sa vzťahuje na staršie overenie. Neboli spustené služby ani zmenené produkčné systémy.

## Receipt a stav prenosu — pôvodné overenie Slizovej úlohy

Prečítané: WORKSPACE.md, projektové AGENTS.md, README.md, PRODUCT.md, DESIGN.md, docs/ARCHITECTURE.md, DISCOVERY.md, PRODUCT_HYPOTHESIS.md, dokumentačný index a frontendové súbory. Overená referencia `frontend/design/vydanie-reference.png`.

Konverzácia „Rozvinúť prvý redakčný frontend Netopiera“ (9. septembra 2026, ID `01a08383-c31f-73b3-b4ee-2906db6f91a1`) bola identifikovaná cez zoznam úloh. Čítací nástroj zlyhal; prijatie prvého návrhu a požiadavka rozvinúť ho boli overené v miestnom kanonickom zázname konverzácie. Surový záznam sa do Linearu neprenáša.

Kontrola 10. septembra: frontend/index.html odkazuje na styles.css a app.js, ktoré v aktuálnom zozname frontendových súborov chýbajú. Ide o rozpracovaný frontend, nie o overenú funkčnú aplikáciu. Backend ani OpenClaw sa pri tejto práci nespúšťali.

Linear, 11. septembra: cez prihlásený web boli vytvorené projekt Netopier (ID `47478718-ae0a-49d6-89bf-e7da59de22e2`) a úloha XDR-142. Spätné otvorenie overilo uložený projektový opis, úplné zadanie úlohy a jej zaradenie do Netopiera. Odkazy sú uvedené vyššie. Projektový opis obsahuje pracovné oblasti; ďalšie samostatné úlohy a míľniky zatiaľ vytvorené neboli. Konektor naďalej hlási potrebu opätovného prihlásenia; úspešný zápis cez web neznamená jeho opravu. Kontrola dokumentačných zmien: `git diff --check`.
