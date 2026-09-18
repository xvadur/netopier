# Rámec skúmania 50 frontendov Netopiera

**Dátum výskumu:** 9. september 2026  
**Stav:** primárne zdroje prečítané; návrh postupu. Tento dokument nedokazuje vytvorenie ani otestovanie frontendov.  
**Cieľ:** pripraviť na jedno ranné rozhodovanie človeka približne 50 funkčných, krásnych a podstatne odlišných podôb slovenského spravodajského webu.

## Odporúčaný postup

Použiť **konečné ľudsky riadené skúmanie dizajnov inšpirované quality-diversity**: desať čitateľských rodín, päť kandidátov v každej, spoločné overiteľné dáta, funkčné skúšky a zachovaná história. Noc rozšíri možnosti; Adam ráno vyberie, ktoré rozpracovať. Krása a vhodnosť pre Adamovu predstavu zostávajú otvoreným ľudským úsudkom.

Rozpočet návrhov rozdeliť na **10 základov + 30 štrukturálnych vetiev + 10 rezervovaných piatych pozícií**. Celý priestor sa nesmie zúžiť po prvých pár modelových kritikách. Agent môže napraviť nečitateľnosť, nefunkčný odkaz alebo zhodnú kompozíciu; nemá podklad na tvrdenie, že pozná Adamov vkus.

Ide o adaptovaný pracovný postup. Vytvorenie galérie s päťdesiatimi návrhmi samo osebe nie je implementáciou MAP-Elites, preferenčnej Bayesovskej optimalizácie ani vedecky validovaným vyhľadávačom krásy. V obmedzenom vyhľadávaní nebol overený konkrétny zavedený framework pod presným názvom „Gaussian loop engineering“. Relevantné overené metódy sú nižšie; Gaussian process je konkrétna súčasť niektorých preferenčných optimalizátorov.

## Čo podporujú primárne zdroje

| Metóda alebo zdroj | Overený mechanizmus | Použitie a hranica v Netopieri |
| --- | --- | --- |
| MAP-Elites, Mouret a Clune, 2015 | Udržiava archív riešení rozdelený podľa zvolených deskriptorov. Nového kandidáta vyhodnotí a vloží do prázdnej bunky alebo ním nahradí slabšieho obyvateľa. Samostatne definuje meranie výkonu a priestor odlišností. | Prevziať ochranu rozmanitosti a explicitné deskriptory. Desať rodín je pracovná taxonómia, nie automaticky vypočítaná mapa. Bez implementovanej reprezentácie, priraďovania buniek a výkonnostnej funkcie nepoužívať tvrdenie „beží MAP-Elites“. [Pôvodný článok a algoritmus](https://arxiv.org/html/1504.04909v1). |
| Preferential Bayesian Optimization, González a kol., 2017 | Učí latentné preferencie z párových porovnaní; využíva Gaussian process model s Bernoulliho likelihood a akvizičné funkcie na výber ďalších porovnaní. | Adamove ranné voľby sú vhodný budúci vstup. Modelové hodnotenie vlastných návrhov nie je údaj o Adamových preferenciách. Pár ručne vybraných duelov ešte nie je tento optimalizátor. [ICML/PMLR](https://proceedings.mlr.press/v70/gonzalez17a.html). |
| CoExBO, Adachi a kol., 2024 | Spája preferenčné učenie s vysvetľovaním výberu kandidátov a pracuje aj s omylmi človeka. Overenie sa týka návrhu lítiovo-iónových batérií. | Prevziať krátke vysvetlenie, prečo sa konkrétna dvojica porovnáva. Teoretické záruky a výsledky pre batérie neprenášať na estetiku spravodajského webu. [AISTATS/PMLR](https://proceedings.mlr.press/v238/adachi24a.html). |
| Walton a kol., verzia 2025 | Štúdia galérií pri návrhu 2D auta zahŕňa 808 účastníkov v teréne a 12 v laboratóriu. Diskusia odlišuje správanie, kognitívne a emocionálne zapojenie; viac výberov z MAP-Elites galérie sa nerovnalo jednotnej subjektívnej preferencii. | Galéria odlišných možností má výskumnú oporu ako pomôcka navrhovania. Výsledok nie je dôkazom estetickej kvality webov ani časovej úspory. Autori uvádzajú obmedzenia generalizácie a vplyv UX samotného nástroja. [Článok, najmä §6.3–6.5](https://arxiv.org/html/2402.07911v2). |
| Anthropic: evaluator–optimizer a evaluácie agentov | Generátor môže iterovať podľa spätnej väzby hodnotiteľa; slučka potrebuje zrozumiteľné kritériá, pozorovanie výsledného prostredia a podmienky zastavenia. Evaluácie rozlišujú výsledok a priebeh, kombinujú programové, modelové a ľudské hodnotenie. | Testy overujú výslednú stránku; modelová kritika je ďalšia vrstva. Obmedziť počet opráv a neuznávať vlastné hlásenie agenta ako dôkaz. [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). |
| maxmilian/loop-engineering | Existujúci verejný skill organizuje slučku okolo kontrolovateľného dokončenia, deterministického overenia, konečných zdrojov a explicitných výstupov. | Použiteľná kontrolná osnova. Nie je algoritmom dizajnového vyhľadávania. Jeho vlastné benchmarkové tvrdenia neboli v tejto práci reprodukované; žiadna inštalácia sa nevykonala. [Repozitár autora](https://github.com/maxmilian/loop-engineering). |

Ďalšie číselné limity a pravidlá v tomto dokumente sú **návrh pre túto úlohu**, nie parametre prevzaté z uvedených štúdií.

## Stabilný obsah a produktová otázka

Všetky návrhy čerpajú z jedného zmrazeného fixture. Pri každom sa má dať zistiť: čo sa stalo, kto konal, čo sa zmenilo, prečo sa udalosť dostala do výberu, ktoré zdroje ju podporujú a čo zostáva neisté. To vychádza z aktuálnej [produktovej hypotézy Netopiera](../PRODUCT_HYPOTHESIS.md), ktorá zároveň oddeľuje faktické zhrnutie, pripísané tvrdenie, komentár a syntézu.

Fixture má obsahovať krátke aj dlhé slovenské titulky s diakritikou, rozličné časy, viaczdrojové udalosti, sporné tvrdenie, aktualizáciu, absenciu fotografie a prázdny výsledok filtra. Pri existujúcich verejných dátach zachovať skutočné URL, čas a identifikátory. Modelové ukážky zreteľne označiť ako ukážky; nevytvárať falošné aktuálne udalosti ani zdroje. Každý variant používa rovnakú revíziu dát a rovnaký referenčný čas. Atraktivita vybranej fotografie ani iný titulok nemajú rozhodovať o porovnaní kompozícií.

Geografická, dátová a grafová rodina sú podmienené obsahom: mapové body vyžadujú podloženú polohu, čísla pôvod a jednotku, graf doložený typ vzťahu. Ak fixture také údaje nemá, použiť vysvetlený prázdny stav alebo explicitne ilustračný scenár. Vizuálna podoba nie je dôkazom existencie backendovej schopnosti.

Zdieľať dáta a interakčné primitíva je rozumné. Spoločný univerzálny page template, v ktorom sa menia iba farby, font a rohy kariet, by nesplnil cieľ.

## Priestor odlišností

Desať rodín má odlišný hlavný vstup do čítania. Názvy slúžia tvorbe a porovnaniu; nemusia sa zobrazovať čitateľovi verejného webu.

| Rodina | Dominantná kompozícia a čitateľský zámer | Príklad podstatnej vetvy |
| --- | --- | --- |
| Novinová titulná strana | Redakčná hierarchia, hlavná udalosť a viac stĺpcov. | Asymetrická titulná strana s jediným dominantným titulkom verzus vyvážené tematické stĺpce. |
| Živý spravodajský prúd | Čas a posledná zmena vedú čítanie. | Súvislá časová os verzus prúd rozdelený na časové vydania s rozbalenými zmenami. |
| Porovnanie zdrojov | Udalosť ako spoločný bod rozličných zdrojových výpovedí. | Paralelné výpovede verzus tvrdenia s rozbalenou oporou priamo pod nimi. |
| Vizuálny magazín | Fotografická a priestorová dramaturgia udalostí. | Veľký obraz s pokračovaním v pásoch verzus sekvencia obrazových esejí s integrovanými zdrojmi. |
| Geografické čítanie | Miesto je navigácia k udalostiam. | Mapa a pevný zoznam verzus redakčný zoznam so synchronizovaným geografickým výrezom. |
| Verejné dáta | Inštitúcia, zmena alebo hodnota tvoria vstup k príbehu. | Záznamový register s vysvetlením zmeny verzus séria dátových príbehov. |
| Konečný briefing | Ohraničený výber, ktorý sa dá dočítať. | Číslované vydanie na jednu stránku verzus postupné karty s jasným koncom. |
| Typografický plagát | Titulok, rytmus a mierka písma vytvárajú hierarchiu. | Monumentálny hlavný titulok verzus striedanie menších blokov a výrazných citácií. |
| Tematické vzťahy | Udalosti sa objavujú cez témy a doložené súvislosti. | Tematická mapa s detailom verzus zoskupené ostrovy udalostí s navigáciou medzi nimi. |
| Čitateľský spis | Hlbší kontext, chronológia a evidencia jednej témy. | Súvislý text s margináliami verzus kapitoly s paralelnou časovou osou a zdrojmi. |

Každý kandidát dostane deskriptory: `family`, `entry_hierarchy`, `page_topology`, `reading_density`, `navigation_pattern`, `time_model`, `media_role`, `evidence_presentation`. Vopred stanovený slovník môže používať kategórie ako jeden prúd, viac stĺpcov, rozdelená obrazovka, sekvenčné vydanie či priestorový prehľad. Tieto deskriptory vyjadrujú zámer; po vykreslení treba overiť, či sa zámer skutočne prejavil.

Nová vetva mení aspoň **dva štrukturálne deskriptory**, pričom aspoň jeden patrí k hierarchii vstupu, topológii stránky alebo navigácii. Typografia, paleta a animácia jej dávajú vizuálny charakter, ale samy osebe nevytvárajú novú koncepciu. Zmenu doložiť jednou vetou „čitateľ teraz začína cez … a pokračuje cez …“ a screenshotom.

Nie je potrebné predstierať metrickú vzdialenosť medzi návrhmi. Zhoda deskriptorov a hash štruktúry môžu odhaliť kandidátov na kontrolu; screenshotové podobnosti sú len indícia. Veľký rozdiel pixelov spôsobený farbou neznamená rozdielny spôsob čítania. Kolízie a posúdené rozdiely sa zachovajú v manifeste.

## Päťdesiat návrhov v troch fázach

| Fáza | Nové pozície | Postup a podmienka pokračovania |
| --- | ---: | --- |
| Základy | 10 | Jeden funkčný základ na rodinu. Vykresliť mobil aj desktop; skontrolovať, že rodina má vlastný spôsob čítania. Najprv pokryť všetkých desať. |
| Vetvenie | 30 | Tri štrukturálne vetvy na každý základ. Prvú zamerať na vstupnú hierarchiu, druhú na priestor/rytmus, tretiu na navigáciu alebo prístup k evidencii. Konkrétne zmeny sú rodinné, nie spoločná sada CSS prepínačov. |
| Piata pozícia | 10 | Jedna na každú rodinu. Prednostne vyriešiť chýbajúci smer alebo rozmanitosť; inak preniesť jednu úspešnú mechaniku z inej rodiny. Kríženie zachová čitateľský zámer hostiteľskej rodiny a uvedie oboch rodičov. |
| Odovzdanie | 0 | Zmraziť stav, dobehnúť overenie, pripraviť porovnateľné náhľady a vysvetliť zostávajúce chyby. Ďalšie návrhy už nepridávať. |

Rovnomerné pokrytie chráni aj neobvyklé smery pred modelovým vkusom. „Úspešná mechanika“ tu znamená funkčnú a zrozumiteľne zdokumentovanú vlastnosť, napríklad prístup ku zdroju bez straty miesta v texte. Neznamená človekom overenú obľúbenosť.

Oprava existujúceho kandidáta má rovnaké ID a novú revíziu; nezapočítava sa ako nový dizajn. Cieľ je 50 platných návrhov. Pri vyčerpaní pevnej hranice je výsledkom pravdivý počet platných, neúplných a odmietnutých pozícií. Päťdesiat nefunkčných alebo len farebne odlišných obrazoviek cieľ nespĺňa.

## Brány a kritika

**Automaticky overiteľné minimum pre každý kandidát:**

1. Existujúca aplikácia sa zostaví, route sa vykreslí a pri stanovených scenároch nevznikne neošetrená chyba ani chýbajúci lokálny asset.
2. Zobrazené texty, časy, počty zdrojov a odkazy sedia na fixture. Nepridali sa nedoložené čísla, vzťahy alebo tvrdenia.
3. Funguje otvorenie udalosti, návrat, prístup ku zdroju a deklarovaná hlavná navigácia. Prítomný filter či vyhľadávanie funguje aj pri nulovom výsledku; dekoratívne tlačidlo sa nevydáva za funkciu.
4. Na mobilnom a desktopovom viewporte nevzniká neúmyselný horizontálny presah, skrytý hlavný obsah ani prekrývanie ovládania. Test reflow na šírke 320 CSS pixelov zahrnie textovú časť; podstatne dvojrozmerné mapy a dáta sa posudzujú s príslušnou výnimkou a dostupnou textovou cestou. [W3C: Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
5. Kontrola kontrastu zistí aspoň základné chyby: bežný text má cieľ 4,5 : 1, veľký text 3 : 1 podľa definície WCAG. Text nad obrázkami si vyžaduje osobitnú kontrolu výsledného vykreslenia. [W3C: Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
6. Hlavný scenár sa dá prejsť klávesnicou, fokus sa nestráca pri otvorení a zatvorení detailu a ovládanie má zrozumiteľné prístupné názvy. Automatizovaný výsledok sa označí rozsahom skutočne skúšaných scenárov.

Náhľady zachytiť v rovnakom prostredí a s rovnakými dátami, veľkosťami viewportu a dokončeným načítaním fontov. Vypnúť automatické striedanie obsahu a animácie počas snímky. Rendering môže závisieť od OS, prehliadača aj hardvéru; vizuálne porovnanie má zmysel pri konzistentnom prostredí. [Playwright: Visual comparisons](https://playwright.dev/docs/test-snapshots).

Praktický balík je 100 titulných náhľadov — desktop a mobil pre 50 kandidátov — plus detail udalosti pre každý kandidát na oboch veľkostiach, najviac ďalších 100. Dodatočné screenshots vytvárať len pri chybe. Automatické accessibility skúšky sú čiastkový dôkaz, nie deklarácia úplného súladu. W3C výslovne vyžaduje aj kvalifikované ľudské posúdenie. [W3C: Evaluating Web Accessibility](https://www.w3.org/WAI/test-evaluate/).

**Modelová vizuálna kritika:** jeden priechod nad screenshotom, krátka odpoveď s tromi časťami: konkrétna silná vlastnosť, najväčší viditeľný problém, jedna navrhnutá oprava. Oddeliť merateľný problém od úsudku o kompozícii. Každé hodnotenie uložiť s označením `model_proxy`, modelom a verziou rubriky. Kritika nesmie premenovať proxy na ľudskú preferenciu ani vyradiť celú rodinu len preto, že je neobvyklá. Automatické skóre krásy sa v rannej galérii nezobrazuje a neurčuje jej poradie.

## Riadenie slučky a pevné konce

Každý cyklus načíta brief, manifest a jednu určenú pozíciu; vytvorí alebo opraví kandidáta, vykreslí ho, preverí brány a uloží dôkazy. Ďalší cyklus pokračuje z tohto stavu. Pred pokračovaním opraví spoločnú chybu jadra, ktorá by inak znehodnocovala všetky varianty. Nevytvára päťdesiat nezávislých build systémov ani databáz.

Navrhované hranice behu:

- **Najviac 50 kandidátskych ID.** K úspechu patria uložené náhľady, manifest, dostupné previews a protokol výsledkov.
- **Najviac dve opravy jednej pozície a 20 opravných cyklov celkovo.** Identická chyba po dvoch opravách uzavrie danú pozíciu ako neúplnú; neprepisuje sa done stav.
- **Časový koniec:** skorší z explicitného ranného termínu a ôsmich hodín od štartu. Posledných 45 minút rezervovať na kontrolu a odovzdanie. Sú to návrhové stropy, ktoré sa zapíšu ako konkrétne časy pri štarte, nie prísľub presného času dokončenia.
- **Spotreba:** používať platný limit zadania a priebežne ukladať dostupné tokenové/časové metriky. Pri limite účtu neobchádzať zastavenie iným účtom, resetom alebo plateným volaním bez oprávnenia. Ak presná tokenová spotreba nie je dostupná, uviesť túto medzeru a ponechať pevný limit cyklov a času.
- **Bez pokroku:** tri po sebe idúce cykly bez novej platnej pozície alebo odstránenej konkrétnej chyby zastavia generovanie. Zachovať stav, príčinu a ďalší potrebný zásah.
- **Lokálny 16 GB Mac:** pred dávkou odčítať záťaž. Najviac jeden build a jeden proces prehliadača s dvoma otvorenými stránkami pre QA súčasne. Pri systémovom memory pressure alebo opakovanom páde zastaviť dávku; neukončovať cudzie procesy.
- **Vlastníctvo:** zapísať vlastné PID, port, dočasné cesty a spôsob ukončenia. Použiť existujúcu vhodnú preview službu. Po práci ukončiť vlastné dočasné QA procesy; trvanie preview pre ranný výber evidovať podľa autorizovaného behu.
- **Hranica produktu:** neštartovať zber Netopiera, neobnovovať vyradený v0, neposielať správy, nepublikovať ani nenasadzovať ako vedľajší účinok hľadania vzhľadu.

Osem hodín nie je povinnosť vypĺňať čas. Ak je päťdesiat návrhov s požadovanými dôkazmi pripravených skôr, slučka sa skončí. Rozšírenie počtu alebo nové kolo po rannom výbere je samostatné pokračovanie.

## Manifest a rodokmeň

Použiť jeden manifest v existujúcom výstupnom adresári frontendového experimentu. Záznam kandidáta obsahuje:

```text
id, revision, family, phase, parent_ids
descriptors, intended_structural_difference, observed_difference
fixture_hash, content_reference_time, public_source_ids
code_path, code_hash, asset_paths, asset_provenance
generator_model, generator_version_if_available, prompt_recipe_version
created_at, updated_at, elapsed_seconds, usage_if_available
status: planned | built | verified | incomplete | rejected
gate_results, test_environment, screenshots, preview_route
critique: { kind: model_proxy, model, rubric_version, observations }
repair_count, failure_reason
human_selection: null | { timestamp, comparison_ids, choice, reason }
```

Rozlíšiť plánovaný descriptor od výsledku po renderovaní. Stabilné ID nepremiestňovať na iný koncept. Revízie nahradené opravou nemať za nové návrhy, ale zachovať ich identitu a dôvod zmeny. Neznámy modelový údaj označiť ako neznámy; nevymýšľať presný snapshot ani spotrebu. Verejné zdroje v manifeste sú obsahová evidencia; záznam modelovej kritiky je samostatná odvodená vrstva.

## Ranný výber v dvoch mierkach

Ráno najprv zobraziť pevnú galériu všetkých 50 návrhov po rodinách, s rovnakou veľkosťou náhľadov, prepnutím mobil/desktop a krátkou vetou o spôsobe čítania. Nezobrazovať priebežné preskupovanie ani skóre modelu. Všetky návrhy zostávajú dostupné; prvá skrátená prehliadka ponúkne po jednom reprezentantovi z každej rodiny a vstup do jej piatich variantov.

Adam môže označiť 6–10 kandidátov a pri ľubovoľnom uviesť, ktorá vlastnosť ho zaujala. Potom 8–12 párových porovnaní so zameniteľnou ľavou a pravou stranou, rovnakou ukážkovou udalosťou a voľbou „ľavý“, „pravý“, „rovnako“ alebo „ani jeden“. Je to dobrovoľný rozpočet na rýchle rozhodnutie, nie podmienka používania galérie ani dôkaz úplného rebríčka.

Porovnania oddelia dve otázky: vizuálnu preferenciu a použiteľnosť konkrétneho čítania. Pri 2–3 finalistoch si Adam otvorí udalosť, nájde jej oporu a vráti sa do kontextu. Spolu s voľbou sa uloží dôvod, napríklad hierarchia titulkov, hustota, pokoj pri čítaní, jasnosť zdrojov či charakter značky. Jedna protichodná voľba nie je chyba používateľa; môže závisieť od obsahu alebo úlohy.

Výsledok môže byť jeden smer, dva finalisti alebo kombinácia pomenovaných mechaník. Až potom má zmysel ďalšie úzke kolo. Skutočný preferenčný Bayesovský model by navyše vyžadoval reprezentáciu kandidátov, model a kernel, spracovanie šumu/remíz, akvizičnú stratégiu a overenie predikcií na zadržaných ľudských voľbách. Na prvý výber z 50 možností jeho zavedenie nie je potrebné.

## Dôkaz dokončenia a záznam tejto práce

Beh možno označiť ako pripravený na výber po prečítaní uloženého manifestu, otvorení galérie, náhodnom otvorení niekoľkých preview a potvrdení presných počtov. Výsledok má uviesť: vytvorené / funkčne overené / vizuálne skontrolované / čakajúce na ľudský výber. Overenie frontendových prototypov neznamená produkčne overenú redakciu ani backend.

Pri tomto výskume boli prečítané `WORKSPACE.md`, aktuálne `AGENTS.md`, `README.md`, `docs/README.md`, `docs/PRODUCT_HYPOTHESIS.md`, existujúca konvencia výskumných poznámok a primárne zdroje odkazované vyššie. Vznikol iba tento dokument. Nevykonali sa úpravy UI/backendu, inštalácie, spustenie služieb ani externé mutácie. Existujúca produktová hypotéza a Discovery neboli touto poznámkou zmenené.
