# Netopier — discovery

Založené: 5. septembra 2026

Živý pracovný dokument na spoločné objavovanie potenciálu Netopiera. Zapisujeme sem možnosti, otázky a postupne overené zistenia. Návrhy v tomto dokumente nie sú automaticky rozhodnutím implementovať ani dôkazom hotovej schopnosti.

## Zámer: spravodajstvo 2026

Verejné správy, vyjadrenia politikov, tlačovky, vládne dokumenty, registre a štatistiky obsahujú veľké množstvo informácií potrebných na prehľad o štáte a svete. Jeden človek ich nedokáže všetky priebežne čítať, počúvať, porovnávať a vyhodnocovať.

Netopier má túto prácu vykonávať priebežne pomocou AI a sprístupňovať výsledky v jednom rozhraní. Má prepájať pôvodné vyjadrenia, dokumenty, dáta a mediálne pokrytie, uchovávať ich históriu a umožniť klásť otázky nad dohľadateľnými dôkazmi.

Redakčná fronta, verejný feed a podklady pre články sú možné výstupy tohto systému. Rozsah discovery zahŕňa aj samotný prehľad, sledovanie aktérov a tém, porovnávanie zdrojov a výskum.

## Aktívna discovery: aké verejné dáta vieme ťahať a aké chceme ťahať

Doplnené 5. septembra 2026: najbližšou úlohou discovery je zmapovať dostupné verejné dáta a vybrať, ktoré z nich má Netopier získavať. Rozsah zahŕňa Slovensko aj medzinárodné zdroje pre prehľad o svete.

### Aké dáta vieme ťahať

Pri každom konkrétnom zdroji zistiť:

- prevádzkovateľa, adresu zdroja a aké údaje skutočne poskytuje;
- cestu získavania: API, RSS, export, verejný web, dokument, titulky alebo audio/video;
- dostupné polia, plný obsah oproti výňatku, históriu, aktualizácie a opravy;
- identifikátory osôb, organizácií, dokumentov a udalostí použiteľné na prepájanie;
- frekvenciu aktualizácie, limity prístupu, podmienky použitia a náklady;
- výsledok malej praktickej skúšky a konkrétne medzery v pokrytí.

Stav prístupu evidovať osobitne: **kandidát → dokumentácia overená → vzorka získaná → pravidelný zber overený**. Verejne viditeľný zdroj ešte neznamená overený automatický prístup k celému jeho obsahu.

### Aké dáta chceme ťahať

Pri každom zdroji určiť, akú otázku nám pomôže zodpovedať, ktorých aktérov alebo tém sa týka a s čím ho chceme prepájať. Rozhodnúť, či potrebujeme priebežný zber, občasnú aktualizáciu alebo získanie až pri výskumnej otázke.

Z doterajšej diskusie chceme preskúmať najmä:

- vlastnú komunikáciu politikov a inštitúcií vrátane Facebooku a tlačoviek;
- rozhodnutia vlády a parlamentu, legislatívu a súvisiace dokumenty;
- verejné peniaze, zmluvy, obstarávania a registre subjektov;
- štatistiky, časové rady a ich metodiku;
- produkciu redakcií: obsah, témy, množstvo, čas, citácie a vývoj pokrytia;
- medzinárodné inštitúcie, dáta a spravodajské zdroje pre sledované svetové dianie.

Konkrétne zdroje a priority ešte vyberieme. Pracovné označenia výberu: **chceme priebežne / chceme na požiadanie / zvažujeme / nezaraďujeme**.

Výsledkom má byť spoločná mapa zdrojov, ktorá pri každom zdroji spája **čo získame, ako to získame, prečo to chceme a čo je už overené**. Podľa nej budeme rozhodovať o konektoroch a spracovaní backendu.

## Potenciál zdrojov a spracovania

| Oblasť | Čo chceme vedieť | Potenciál spracovania | Otvorené overenie |
| --- | --- | --- | --- |
| RSS a redakcie | Čo redakcie hovoria, koľko, o čom a kedy. | Zber, časové porovnania, citované osoby, pôvod tvrdení, vývoj titulkov a pokrytia. | Rozsah RSS oproti plnému textu; úplnosť zachyteného korpusu; dostupnosť a podmienky ďalšieho získavania obsahu. |
| YouTube a tlačovky | Kto čo povedal, oznámil alebo sľúbil. | Dostupné titulky; pri ich absencii prepis dostupného audia, časové značky, rozlíšenie rečníkov, extrakcia výrokov a záväzkov. | Získanie média, kvalita slovenského prepisu, mená, čísla, náklady a podmienky zdroja. |
| Facebook politikov | Čo politik sám publikuje a ako sa jeho komunikácia mení. | Sledovanie verejných stránok, príspevkov a videí; prepojenie s ostatnými kanálmi a mediálnym pokrytím. | Konkrétna cesta prístupu, pokrytie stránok oproti profilom, úplnosť, čerstvosť, cena a podmienky. |
| Vládne a parlamentné dokumenty | Čo bolo navrhnuté, prerokované, schválené a vykonané. | Archivácia verzií, porovnanie zmien, termíny, zodpovedné inštitúcie, väzby na vyjadrenia. | Konkrétne zdroje a formáty; odlíšenie návrhu, rozhodnutia, účinnosti a realizácie. |
| Štatistické úrady a verejné dáta | Čo ukazujú čísla a čo sa v nich zmenilo. | Časové rady, nové vydania a revízie, porovnanie tvrdení s dátami. | Definície ukazovateľov, jednotky, obdobia, metodické zmeny a dostupné rozhrania. |
| Zmluvy, obstarávanie a registre | Kto s kým koná, o aké peniaze ide a čo tomu predchádzalo. | Sledovanie nových záznamov a zmien, prepájanie subjektov, udalostí a dokumentov. | Stabilné identifikátory, kvalita zhôd, dostupnosť histórie a význam jednotlivých záznamov. |

## Sledovať politika znamená sledovať jeho verejné kanály

Politik alebo inštitúcia má mať priradené overené zdrojové účty a kanály. Facebook, YouTube, web, parlamentné vystúpenia a mediálne citácie sa majú stretávať pri tom istom aktérovi a relevantných udalostiach.

Chýbajúci prístup cez jedno API neuzatvára možnosť sledovať daný zdroj. Hľadáme a porovnávame dostupné cesty. Rovnaké vystúpenie na viacerých platformách treba prepojiť, pričom samostatné texty, dodatky a časy publikovania zostávajú zachované.

Systém musí rozlišovať medzi „nebol zachytený nový príspevok“ a „zdroj sa nepodarilo skontrolovať“. Výpadok zberu nesmie vytvoriť zdanlivé ticho aktéra.

### Facebook: nájdené cesty na overenie

Stav k 5. septembru 2026: overená existencia dokumentácie; žiadna z týchto ciest zatiaľ v tejto discovery nebola prakticky otestovaná na slovenských politikoch.

Dve konkrétne služby zaradené do discovery na porovnanie sú **NewsWhip** a **Apify Facebook Posts Scraper**. Zistiť, aké verejné príspevky sledovaných politikov nimi vieme získavať, s akou úplnosťou, oneskorením a nákladmi. Meta Content Library zostáva ďalšou možnou výskumnou cestou.

- **NewsWhip:** dokumentuje Facebook Posts API `/fbPosts` vrátane filtrovania podľa autorov. Overiť konkrétne slovenské stránky, dostupné polia, históriu a cenu. [Dokumentácia](https://developer.newswhip.com/reference/fbposts).
- **Apify Facebook Posts Scraper:** dokumentuje zber verejných Facebook Pages podľa URL; osobné profily sú odlišný prípad a podľa vstupnej dokumentácie nie sú podporované týmto nástrojom. Overiť kvalitu, čerstvosť a úplnosť výsledkov. [Vstupná schéma](https://apify.com/apify/facebook-posts-scraper/input-schema).
- **Meta Content Library a API:** výskumný prístup k verejnému obsahu s podmienkami oprávnenosti. Overiť možnosť prístupu pre projekt alebo partnera a podmienky použitia či exportu dát. [Informácie Meta](https://about.fb.com/news/2023/11/new-tools-to-support-independent-research/).

Technická dostupnosť nástroja a povolenie platformy sú samostatné otázky. Meta uvádza obmedzenie automatizovaného zberu bez svojho povolenia. [Stanovisko Meta](https://about.fb.com/news/2021/04/how-we-combat-scraping/amp/).

## Otázky, na ktoré má systém potenciálne odpovedať

- Čo dnes konkrétny politik komunikoval naprieč svojimi kanálmi?
- Čo vláda skutočne rozhodla a čo zatiaľ iba oznámila?
- Čo sa z predchádzajúceho sľubu uskutočnilo a aké dokumenty to dokazujú?
- Čo sa zmenilo v relevantných štatistikách a zmenila sa aj ich metodika?
- Ktoré redakcie pokryli udalosť, kedy, v akom rozsahu a s akými zdrojmi?
- Kto priniesol vlastné zistenie a kto prevzal rovnaké pôvodné tvrdenie?
- Kde si vyjadrenia, dokumenty alebo dáta odporujú a čo potrebujeme došetriť?
- Čo podstatné pribudlo v dlhodobo sledovanej téme od posledného prehľadu?

## Potenciál prepojenia: jeden príklad

Minister prednesie tvrdenie na tlačovke. Netopier uchová výrok s časovou značkou, pripojí súvisiaci vládny dokument a relevantnú štatistickú sériu. Sleduje následné príspevky ministra a pokrytie redakcií. V jednom pohľade sa dá preskúmať, čo zaznelo, čo je doložené, čo pribudlo a ako bola vec sprostredkovaná verejnosti.

Toto je navrhnutý príklad na overenie celej cesty, nie potvrdený implementačný plán.

## Architektonické otázky

- Ako oddeliť zdrojový záznam, konkrétne tvrdenie, udalosť a dlhodobú tému?
- Ako spoľahlivo priraďovať osoby, funkcie, inštitúcie a účty bez falošných zhôd?
- Ako uchovávať pôvodný obsah, opravy, odstránenia a čas, keď sme zmenu zistili?
- Ako ukladať dôkazy nezávisle od úspechu následného AI spracovania?
- Ktoré spracovanie má bežať priebežne a ktoré až na konkrétnu otázku?
- Ako merať pokrytie zdrojov, oneskorenie, presnosť a prevádzkové náklady?
- Ako odlíšiť počet publikovaní od počtu nezávislých potvrdení?
- Ako vysvetliť výber udalosti do prehľadu a umožniť Adamovi tento výber korigovať?
- Ako bude spoločný základ poskytovať podklady pre Netopier aj Hriech?

## Aktuálne overený základ

Lokálne overené v tejto konverzácii 5. septembra 2026:

- PostgreSQL, Miniflux a API bežali; priebežný worker bol vypnutý.
- Miniflux mal pri kontrole 696 položiek zo štyroch RSS kanálov, bez hlásených chýb ich parsovania.
- Jedna obmedzená dávka spracovala 20 položiek cez archiváciu, embeddingy, stories a events.
- Následný API smoke test prešiel: archív mal 76 článkov, 68 stories a 71 eventov.
- Tieto výsledky dokazujú fungovanie jednej lokálnej dávky a projekcie dát. Nedokazujú úplnosť zberu, správnosť všetkých priradení ani vyššie opísané nové schopnosti.

## Ďalšie potencie a poznámky

Sem budeme priebežne dopĺňať ďalšie možnosti, príklady a upresnenia zo spoločnej diskusie.

### 6. september 2026 — pôvodné vystúpenie a následné mediálne podanie

Adamova explicitná požiadavka: Netopier má priebežne zachytiť nové verejné politické vystúpenie na YouTube, spracovať časovo ukotvený prepis a vytvoriť udalosť bez čakania na mediálny článok. K nej má postupne pripájať články, reakcie, ďalšie vyjadrenia a relevantné štátne dokumenty či dáta. V jednom pohľade má byť dostupný pôvodný obsah, následné pokrytie a dôkazmi podložená syntéza. Presné kanály, interval kontroly a prípustné oneskorenie ešte nie sú určené; tento zápis nezapína monitoring.

Motivačným príkladom je Adamom opísaný rozdiel medzi debatou Šimečku s Dankom a jej podaním v súmare víkendových relácií Denníka N. Konkrétne video ani článok neboli v tejto konverzácii identifikované a porovnané. Hodnotenie výkonu a hypotéza preferencie redakcie sú podnetom na overenie, nie zistením Netopiera.

Požadovaný predmet sledovania zahŕňa aj výber citácií, hodnotiace označenia, pripisovanie zodpovednosti, mieru istoty alebo pochybnosti, ospravedlňujúci kontext a podstatné vynechania. Každé zistenie musí umožniť prechod z konkrétnej pasáže článku na príslušný úsek pôvodného záznamu. Rozlišovať autorov text, citáciu hosťa a žáner článku. Neúplný RSS výňatok nestačí na záver, že článok niečo vynechal.

Návrh overenia: najprv jedna celá relácia a jej mediálne pokrytie; následne vopred vymedzený korpus, napríklad 100 politických článkov. Skúmať rovnaké jazykové a dôkazové kritériá pri porovnateľných situáciách naprieč aktérmi, vrátane protipríkladov. Samotný pomer pozitívnych a negatívnych zmienok nedokazuje neodôvodnenú preferenciu; treba zohľadniť pôvodné konanie, obsah, tému a žáner. Úmysel redakcie sa z rozdielneho podania automaticky nevyvodzuje.

Návrh spracovania: reláciu zachovať ako celok, jednotlivé tvrdenia a udalosti v nej samostatne prepojiť s časovými úsekmi. Štátne zdroje môžu zakladať vlastné udalosti aj overovať konkrétne tvrdenia; nie sú iba prílohou mediálneho pokrytia. Syntéza odlišuje výrok, doložený stav, redakčné hodnotenie a otvorenú otázku. Pri hodnotení celého debatného výkonu zachovať odkaz na audio/video; textový prepis nezachytáva všetky jeho vlastnosti.

Kontrola kódu 6. septembra 2026: `pipeline.py` spracúva položky Minifluxu cez `ArticleArchive`; `StoryEngine.atomize` vytvára kandidátov z `article_revisions.rss_content_text`. Eventová vrstva existuje. V aktuálnom `src/netopier` nie je implementovaný reťazec YouTube → časovaný prepis → udalosť ani porovnanie prepisu s redakčným podaním. Runtime sa pri tejto kontrole nemenil ani netestoval.

Navrhovaný dôkaz dokončenia prvého rezu: nové video zo zvoleného verejného kanála sa zachytí v dohodnutom intervale; originál a verzovaný prepis sú uložené s provenienciou; udalosť vznikne bez článku; neskoršie pokrytie sa pripojí k správnej udalosti a porovnanie odkazuje na presné pasáže. Chýbajúci alebo chybný prepis musí byť viditeľný ako stav spracovania, nie ako ticho aktéra. Záznam zdroja nesmie čakať na úspech AI syntézy.
