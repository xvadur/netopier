# AI newsroom a Natural20: teardown pre Netopier

**Stav overenia:** 3. september 2026  
**Rozsah:** Natural20, fungujúce AI news produkty, autonómne publikačné experimenty, agentické newsroom produkty a prenositeľné open-source komponenty  
**Účel:** zistiť, čo už existuje pre model „stroj zachytí dianie, Adam kurátoruje, systém navrhne research a pripraví verejný výstup“

## Záver

Natural20 je reálny a aktuálne fungujúci **eventový AI agregátor s vlastnou obsahovou nadstavbou**, nie kompletná redakcia s ľudským kurátorom. Jeho hlavný mechanizmus je transparentný: zbiera približne 200 položiek z RSS, laboratórií, Hacker News, Redditu a arXivu, zoskupuje podobné titulky do udalostí a radí ich podľa „momentum“ — šírky pokrytia, sociálnej odozvy, Google Trends a čerstvosti. Prevádzkovateľ výslovne píše, že skóre nepredikuje pravdu. To je dobrý vzor pre verejný živý wire, no nedokáže vyriešiť Adamovu otázku, či je udalosť relevantná pre Netopier.

Najbližší verejný technický analóg celého Adamovho konceptu nie je jeden produkt, ale kombinácia:

- **Natural20 / Heatwire / StackBrief** pre eventový live wire, zhlukovanie a rýchly verejný povrch;
- **AI·HOT** pre explicitnú editoriálnu politiku, feedback `👍 / 👎 / ⭐`, poznámky a návrh novej verzie politiky na ľudské schválenie;
- **News Minimalist** pre oddelenie významnosti od osobnej dôležitosti a lacné dvojstupňové skórovanie;
- **HuggingNews** pre krátku strojovo napísanú správu z primárnych zdrojov, roly zdrojov a presné citáty;
- **NEWSCOPE** pre výber komplementárnych odsekov a perspektív namiesto desiatich parafráz tej istej informácie;
- **The Machine Herald** pre nemenné revízie, kontrolovaný publikačný prechod, provenance a korekcie ako nové záznamy;
- **Particle** pre čitateľský produkt: jedna udalosť, viac zdrojov, entity, citáty, dokumenty, časová os, otázky a personalizácia.

Existujú aj produkty, ktoré sa priamo predávajú ako autonómna redakcia — Mastheads, Beatwire, A47, Newsroom AIOS — ale ich verejné tvrdenia nie sú otvorenou architektúrou ani nezávislým auditom kvality. Sú vhodné na produktový teardown, nie ako dôkaz, že „objektivita a fact-checking“ sú vyriešené.

Pre Netopier z toho vyplýva jasný produktový model: **event intelligence zostáva jadrom; nad ňou vznikne verzovaná Adamova redakčná politika, súkromná kurátorská fronta a samostatná research lane.** Verejný feed môže byť rýchly a prevažne automatický, ale význam, overenosť a Adamov záujem musia byť tri samostatné skóre.

## Rozlíšenie pojmov

| Typ | Čo robí | Overené príklady |
|---|---|---|
| AI agregátor | zbiera existujúce položky, deduplikuje, zhlukuje, radí a odkazuje na pôvodné zdroje | Natural20, AI Newsnow, Heatwire, StackBrief |
| AI sumarizátor / čitateľský produkt | nad viacerými článkami vytvára stručnú syntézu, otázky, citáty a personalizovaný feed | Particle, News Minimalist |
| AI wire | z primárnych zdrojov strojovo napíše nový krátky faktický záznam s citáciami | HuggingNews |
| agentická redakčná stavebnica | monitoring → výber → research/verifikácia → draft → review → CMS/publikácia | AI·HOT, HeadlinesForge, Mastheads, Beatwire, A47 |
| autonómna publikácia | AI vyberá, píše, kontroluje a publikuje vlastné články | The Machine Herald; komerčne to deklarujú Mastheads a A47 |
| výskumný komponent | rieši jednu časť, napríklad diverzitu retrievalu, nie newsroom ako produkt | NEWSCOPE |

Tieto kategórie sa prekrývajú. Marketingový názov „AI newsroom“ sám osebe nehovorí, či systém robí pôvodné reportovanie, iba prepisuje zdroje, alebo má reálnu schvaľovaciu a korekčnú cestu.

## Natural20: čo presne robí

### Pozorovaný produktový tok

```text
15+ deklarovaných source skupín
  -> raw položky z RSS / labs / HN / Reddit / arXiv / newsletterov
  -> source score + display rescore podľa engagementu a čerstvosti
  -> title similarity + entity/topic normalization
  -> event cluster
  -> bigness 0-100 podľa coverage, HN, Reddit, Trends a recency
  -> Top Stories + Live Wire + cluster detail s receipts
  -> občas samostatný dlhší Natural20 coverage článok
  -> RSS / verejný JSON / newsletterový ekosystém
```

[About](https://natural20.com/about) deklaruje viac než 15 zdrojových skupín, vyše 200 správ denne, päťminútové aktualizácie, multi-source clustering a pipeline udržiavanú agentmi bez editoriálneho tímu a manuálnej kurácie. Kontrolovaný [verejný JSON feed](https://natural20.com/api/feed) mal čas generovania a 200 položiek s `title`, `url`, `source`, `sourceType`, `published`, `summary` a `score`. Hlavná stránka v tom istom čase projektovala 181 udalostí/položiek, Top Stories, Live Wire, „Our Stories“, „Curated Feed“, Lab Watch a latest paper.

[Metodika skórovania](https://natural20.com/how-scoring-works) je mimoriadne užitočná, pretože pomenúva účel bez marketingovej hmly: Natural20 „nemeria pravdu, ale momentum“. Raw položka dostáva source score; display poradie pridáva HN/Reddit a recency boost. Cluster vzniká z podobnosti titulkov a normalizácie entít/tém. Jeho `bigness` váži coverage `3.0`, Hacker News `2.0`, Reddit `2.0`, Google Trends `1.5`; Twitter je rezervovaný a nepoužitý. Dve, tri a päť zdrojov pridávajú bonus, nový cluster dostáva dočasný freshness boost.

Detail eventu poskytuje:

- prvý a posledný zachytený čas;
- hlavný titulok a krátku syntézu;
- lead source;
- bigness a čiastkové coverage/HN/Reddit/Trends signály;
- všetky „receipts“ s vydavateľom, časom, score, titulkom, úryvkom a odkazom na pôvodný článok.

Toto je silná verejná gramatika pre Netopier: jeden event, rýchla orientácia a pod ním rozbaliteľné dôkazy. Nie je to však claim ledger ani fact-check.

### Konkrétne obmedzenie clustra

Kontrolovaný top cluster „Nvidia confirms it will buy Hugging Face for $12.9 billion“ obsahoval šesť položiek. Päť bolo o akvizícii; šiesta bola „China on the Hugging Face Incident“ z ChinaTalk s nesúvisiacim perexom o pekinskom rámcovaní AI safety. Je to priamo pozorovaný false merge, pravdepodobne spôsobený spoločnou entitou a podobnosťou titulku. Práve preto Netopier správne považuje false merge za drahší než false split a potrebuje event features, čas, aktérov, akciu a ľudské merge/split lineage, nie iba titulkový centroid.

### Obsah, provenance a objektivita

Natural20 má dve odlišné obsahové vrstvy:

1. live agregované eventy s linkami a receipts;
2. vlastné dlhšie `coverage` texty s referenciami.

Skontrolovaný dlhý text o Anthropic mal deväť záverečných referencií a časovú os, no zároveň používal silné hodnotiace formulácie a špekulatívny záver. Je to analýza s postojom, nie neutrálna wire správa. Na článku nebola v kontrolovanom strojovom výstupe viditeľná osobná autorská byline ani samostatný item-level štítok „AI-generated“; site-wide footer a About však otvorene hovoria „Powered by AI agents“ a „No editorial team“.

Pre Netopier treba zachovať ostrejšiu hranicu:

- `event_summary` = zdrojovo ohraničený opis udalosti;
- `Adam_note` = pomenovaný komentár/postoj;
- `research_brief` = syntéza s claim/evidence mapou;
- `published_article` = schválená nemenná revízia.

### Personalizácia a business model

Na verejnom Natural20 sú doložené search a filtre podľa source typu, kľúčového slova a témy. Verejná dokumentácia nepopisuje profil záujmov, kurátorský inbox, spätnú väzbu na ranking ani osobnú research frontu. `My Benchmarks` nie je dôkaz personalizovaného news feedu.

Samotný real-time agregátor nemá na kontrolovaných stránkach doložený samostatný cenník. Širší Natural20 ekosystém však zahŕňa [newsletter](https://course.natural20.com/) s platenými partnerstvami/reklamnými blokmi a výzvami do komunity/AI University. Bez interných účtov nemožno určiť, aká časť príjmu pochádza z reklamy, komunity, YouTube alebo iných liniek. Doložený je teda **media funnel**, nie unit economics agregátora.

## Najrelevantnejšie fungujúce produkty

### HuggingNews — najčistejší analóg strojovej wire správy

[HuggingNews About](https://huggingnews.com/about) opisuje pipeline: sleduje účty, laboratóriá, projekty, reportérov a výskumníkov; hľadá multi-source clustre; pri novej udalosti robí research a píše krátku správu; následne ukazuje zdrojový materiál, rolu zdroja, pull quote a originálny link. Každá správa má témy, tagy, entity a filtre podľa firmy, osoby či produktu. Feed sa aktualizuje priebežne cez deň a má Atom výstup.

To je veľmi blízko želanému „čo povedal Fico?“: samostatne ukladať hovoriaceho, exact quote, rolu zdroja (`source`, `analysis`, `support`), čas a link. Personalizácia je podľa prevádzkovateľa ešte len pripravovaná. Verejne nie je doložený editoriálny feedback loop ani otvorená licencia.

### Particle — najlepší čitateľský story detail

[Particle](https://particle.news/blog/introducing-particle-the-news-organized) zoskupuje pokrytie do stories a ponúka viac sumarizačných režimov (`5Ws`, jednoduché vysvetlenie, opposite sides), otázky nad udalosťou, follow osoby/miesta/veci/autorov/vydavateľov, dôležité citáty s kontextom, originálne dokumenty a časovú os príbuzných udalostí. Tvrdí kombinovaný ľudský a automatický dohľad a ukazuje linky na zdroje. V roku 2026 má iOS aj Android a partnerstvá s Reuters a The Atlantic; firma oznámila seed 4,4 mil. USD a Series A 10,9 mil. USD.

Particle je dobrý produktový benchmark pre verejný Netopier, no nie kódová stavebnica. Je proprietárny a jeho interné accuracy čísla sú first-party tvrdenie, nie nezávislý audit.

### News Minimalist — filter typu „požiar v Gelnici nejde hore“

[News Minimalist](https://www.newsminimalist.com/about) deklaruje analýzu približne 30-tisíc článkov denne v 12 jazykoch a skóre významnosti 0–10. Model oddeľuje spoločenskú významnosť od osobnej relevantnosti cez scale, impact, novelty, future potential, legacy, positivity a credibility. Drahší model vytvoril historické označenia; lacnejší model sa ich učí replikovať vo veľkom. Obsah pod 3 má typicky šport, zábavu a malé lokálne udalosti; verejný RSS prah 5,5 dá približne desať správ týždenne. Premium umožňuje krajiny, kategórie, prahy, blokované slová a coverage filtre; Pro pridáva intent monitoring v prirodzenom jazyku.

Netopier potrebuje podobný lacný triage mechanizmus, ale jeho relevance je politicko-inštitucionálna, nie globálna. Lokálny požiar môže zostať nízko, kým nevznikne ministerská reakcia, systémové zlyhanie, verejný výdavok, politické zneužitie alebo rozpor medzi zdrojmi.

### AI Newsnow — hotový story-centric live pattern

[AI Newsnow](https://ainewsnow.io/about) každých desať minút číta 273 kurátorovaných zdrojov, zhlukuje ich do stories a radí podľa source tieru, počtu vydavateľov, prítomnosti primárneho oznámenia, launch jazyka a recency. Výslovne nepoužíva engagement ani personalizáciu. Má denný AI brief, verejný JSON, RSS pre sekcie, live health zdrojov a publisher opt-out. Je to agregátor s čistým kontraktom, nie redakcia ani research systém.

## Autonómna redakcia a editoriálna slučka

### AI·HOT / AX's AI RADAR — najdôležitejší donor konceptu

[AI·HOT](https://github.com/xingfanxia/newsroom) je verejná Next.js/Turso aplikácia pre editorov a analytikov. Ingestuje RSS, Atom, RSSHub, API a scraping; LLM vytvára bilingválny summary, komentár, importance 0–100, taxonómiu a clustre. Najhodnotnejší mechanizmus je verzovaná editoriálna politika:

- editor dá `👍 / 👎 / ⭐` a poznámku;
- Claude agent číta nahromadený feedback;
- pripraví diff `editorial.skill.md`;
- človek diff schváli;
- workery načítajú novú verziu v ďalšom enrichment kole.

Politika obsahuje score bands, hard exclusions, pozitívne signály, taxonómiu, oddelený faktický summary/editor note/sharp analysis a disciplínu proti overfittingu: menej než päť feedbackov nestačí na zmenu a jednotlivé prípady sa majú preložiť do pravidla. Admin surface ukazuje náklady LLM, zdrojové zdravie, queue, cron, chyby, policy diff a históriu iterácií.

Toto je prakticky Adamova hypotéza premenená na produktový mechanizmus. Treba prevziať **koncept**, nie kód: GitHub pri kontrole neidentifikoval licenciu a v koreni nebol viditeľný `LICENSE`, takže verejná dostupnosť repozitára nedáva právo kopírovať implementáciu. Repo bolo vytvorené v apríli 2026, posledný zistený push bol 2. augusta 2026 a malo iba dve hviezdy; je aktívny experiment, nie vyzretý štandard.

### The Machine Herald — provenance a publikačný ledger

[The Machine Herald](https://machineherald.io/about/) sa označuje za autonómny newsroom: bot vytvorí podpísaný submission, validátor overí schema/source count/URL/signature/hash, Chief Editor AI urobí review, vznikne provenance record a článok sa publikuje cez GitHub/Cloudflare. Vyžaduje minimálne dva HTTPS zdroje z allowlistu a zdroje archivuje. Opravy nemenia pôvodný článok; vzniknú ako nový záznam s väzbou na originál.

[MIT repozitár](https://github.com/the-machine-herald/machineherald.io) má oddelené submissions, articles, provenance a reviews, editoriálnu politiku a source allowlist. Verejná dokumentácia však ukazuje dôležitú nuansu: AI pripraví review, ale ľudský maintainer schválený PR merguje. „Zero human editorial intervention“ preto znamená, že človek nepíše ani obsahovo needituje, nie že v publikačnej ceste neexistuje ľudský operátor.

Pre Netopier je hodnotná nemennosť, podpis/hash, oddelený review artifact a correction lineage. Menej vhodná je filozofia úplného odstránenia ľudského úsudku — Adamova kurácia je zámerný zdroj hodnoty.

### Komerčné „celé newsroomy“

- [HeadlinesForge](https://headlinesforge.com/) deklaruje päť krokov Discover → Verify → Draft → Edit → Hand off, monitoring webu/TV/rádia/social, multi-source fact a quote checks a povinné editor approval. Je to najbližší komerčný opis human-in-the-loop Netopiera.
- [Mastheads](https://mastheads.app/features) deklaruje topic discovery, research, independent gates, drafts, WordPress/Ghost, export/API, visible provenance, editor of record a označovanie bezobslužne publikovaných článkov. Uvádzané náklady, počty článkov a kvalita sú first-party marketingové tvrdenia.
- [Beatwire](https://www.beatwire.ai/) deklaruje radar z RSS/Reddit/X/YouTube, cross-source cluster, signal/velocity score, story builder, desk a manuálny/asistovaný/auto publish režim. Verejný web nepotvrdzuje otvorený kód ani interný eval.
- [A47](https://a47media.com/) deklaruje šesť agentov od monitoringu po multi-format publish a vlastný živý autonómny outlet. Čísla o 12 minútach, 0,1 % korekciách a 15-tisíc článkoch pochádzajú od firmy a neboli v tomto audite nezávisle overené.

Tieto produkty dokazujú, že kategória už existuje. Nedokazujú, že automatická verifikácia vyriešila zdrojovú závislosť, false merge, právny status alebo zodpovednosť.

## Open-source stavebné bloky

Aktivita je snapshot k 3. septembru 2026. Hviezdy nie sú kvalita; last push nie je bezpečnostný audit.

| Projekt | Typ a stack | Licencia / aktivita | Prenositeľná časť | Rozhodnutie |
|---|---|---|---|---|
| [Heatwire](https://github.com/NinjaCodeTurtle/heatwire) | Next.js 15, Postgres 16, pgvector, one-shot worker; RSS/HN → embed → cluster → LLM curate → heat | MIT, názov/wordmark vylúčený; pri kontrole 0 stars | time-windowed event centroid, LLM len na borderline merge, source-domain independence, decay heat, JSON/RSS contract | Najbližší kódový referenčný donor pre event feed; nekopírovať celý runtime do v1 |
| [StackBrief / AI News Ranker](https://github.com/AlexK020908/AI-News-Ranker) | Next.js, Supabase/Postgres/vector, Redis; približne 130 AI zdrojov | Apache-2.0; 2 stars pri kontrole | source cadence, raw XML, story buckets, region, topic engagement, web/worker split | Čítať schema/API a frontend panels; názov StackBrief je kolízny s inými produktmi |
| [AATF AI News Aggregator](https://github.com/flyryan/ai-news-aggregator) | Python multi-agent gather/analyze/synthesize + Svelte SPA | Apache-2.0; last push 3. 9. 2026; 23 stars/7 forks | continuity labels, checkpoint/resume, per-phase cost/status, daily briefing, replay reálnych LLM behov | Donor observability a research orchestration, nie live-minúta runtime |
| [Beehive](https://github.com/sinmentis/beehive) | FastAPI/SQLite personal briefing a bounded Research Sessions | MIT; alpha 0.1.0, maintainer tvrdí vlastné production use | ranked owner inbox, unread/votes, queued deep read, viditeľný research plán, tvrdé budget caps, source deactivation bez straty histórie | Donor súkromnej kurátorskej a research lane; nezamieňať s event core |
| [AI·HOT](https://github.com/xingfanxia/newsroom) | Next.js/Turso, enrichment workers, policy iteration agent | **licencia neurčená** | feedback → policy diff → human approval → versioned runtime policy | Prevziať mechanizmus a vlastné typy, nie zdrojový kód |
| [The Machine Herald](https://github.com/the-machine-herald/machineherald.io) | Astro, GitHub PR/Actions, Ed25519 provenance | MIT; verejný repo a živý web | immutable submission/review/publish artifacts, source allowlist, hash/signature, correction lineage | Vhodný donor publication ledgeru |

## NEWSCOPE: čo rieši pre research lane

[NEWSCOPE paper](https://aclanthology.org/2025.emnlp-main.1722/) nie je newsroom produkt. Je to dvojstupňový retrieval postup pre jednu udalosť:

1. dense retrieval vyberie relevantné odseky;
2. v odsekoch sa embedujú a clusterujú jednotlivé vety;
3. diversity-aware reranking vyberie odseky pokrývajúce nové sentence clusters;
4. výsledok maximalizuje relevanciu aj pokrytie rozdielnych aspektov.

Toto presne patrí medzi event cluster a research brief. Klasický similarity search vracia desať verzií tej istej agentúrnej vety. NEWSCOPE-like selector má vyberať primárne rozhodnutie, reakciu opozície, právny mechanizmus, číslo, časový kontext a protiargument — ak sú v dôkazoch — namiesto redundantných parafráz. Paper zavádza interpretable metriky pairwise distance, positive cluster coverage a information density ratio; tie sú vhodnejšie pre research-pack eval než obyčajný top-k recall.

## Produktový návrh pre Netopier

### Tri skóre, ktoré sa nesmú zliať

| Skóre | Otázka | Typické signály |
|---|---|---|
| `event_confidence` | Je to tá istá udalosť a je dostatočne doložená? | identity, čas, miesto, aktéri, akcia, source-family independence, rozpory |
| `public_consequence` | Aký verejný dosah má udalosť? | právna/inštitucionálna zmena, peniaze, počet zasiahnutých, rozhodovacia moc, trvanie, precedent |
| `adam_relevance` | Patrí to do Adamovej redakčnej pozornosti? | watchlist, tézy, osoby, inštitúcie, médiá, predchádzajúce zásahy, explicitný feedback |

Natural20 `bigness` môže byť štvrtý pomocný signál `attention_momentum`. Nesmie rozhodovať sám: desať prepisov agentúrnej správy nie je desať nezávislých potvrdení a virálnosť nie je verejný následok.

### Pravidlo pre „požiar v Gelnici“

Samotná lokálna nehoda ide do archívu a ostáva mimo Adamovej priority. Eskaluje sa, ak sa objaví aspoň jeden redakčne relevantný mechanizmus:

- koná alebo sa vyjadruje minister, vláda, polícia, prokuratúra, samospráva či iná sledovaná inštitúcia;
- udalosť odhaľuje systémový problém, opakovaný vzorec, verejné peniaze alebo regulačné zlyhanie;
- politik alebo médium ju používa ako dôkaz pre širšie tvrdenie a treba overiť mechanizmus;
- zdroje si odporujú v príčine, následku, počte obetí, právnom stave alebo zodpovednosti;
- Adam podobné udalosti opakovane vyberá alebo explicitne založí watch rule.

Toto musí byť verzované pravidlo s dôvodom `why surfaced`, nie skrytá modelová intuícia.

### Súkromná kurátorská plocha

```text
incoming events
  -> machine triage
  -> Adam inbox: NOW / WATCH / RESEARCH / LOW
  -> open evidence
  -> comment / save / dismiss / escalate / merge-split
  -> structured feedback reason
  -> proposed policy diff
  -> Adam ratification
```

Každá karta potrebuje udalostný titulok, čo je nové, kto konal/povedal, čas, počet nezávislých source families, dôkazovú silu, rozpory, momentum, dôvod zaradenia a presné akcie. Klik na `research` nesmie spúšťať neobmedzeného agenta; vytvorí trvalý case s otázkou, plánom zdrojov, rozpočtom, stavom a výsledným evidence packom.

### Research lane

```text
event / Adam question
  -> research case
  -> explicit questions + falsifiers
  -> approved source plan
  -> bounded collection
  -> claim / quote / document extraction
  -> diverse evidence selection
  -> gaps and contradictions
  -> evidence pack
  -> Adam position
  -> article contract / draft
```

Beehive ukazuje užitočný pattern viditeľného plánu a tvrdých limitov. NEWSCOPE rieši informačnú rôznorodosť. Machine Herald ukazuje nemenné revízie. Žiadny z nich sám nedodáva Netopierov celý workflow.

## Čo adaptovať a čo odmietnuť

### Adaptovať

- Natural20: cluster detail, receipts, first/last seen, verejná scoring metodika, JSON/RSS.
- AI·HOT: policy-as-text, feedback dôvody, policy diff, minimálny feedback pred zmenou, ľudské schválenie.
- HuggingNews: source roles, exact quotes, entity/person/product filtre, krátka wire jednotka.
- News Minimalist: drahý teacher → lacný triage model a explicitné faktory významnosti.
- Particle: story Q&A, entity pages, quotes, documents, related timeline a control over interests.
- Machine Herald: nemenné submission/review/publish revízie, provenance a correction lineage.
- Heatwire: source-domain independence a LLM iba na ohraničené sporné prípady.
- NEWSCOPE: diversity-aware evidence pack.

### Odmietnuť

- počet publikujúcich domén ako automatický dôkaz pravdy;
- auto-publish bez pomenovaného človeka zodpovedného za verejný výstup;
- jeden modelový score, ktorý mieša podobnosť udalosti, popularitu, dôveryhodnosť a Adamov záujem;
- „AI objektivitu“ ako marketingové tvrdenie bez oddelenia faktu, atribúcie, interpretácie a neistoty;
- generické fiktívne AI persony ako náhradu transparentnej syntetickej byline a Adamovho komentára;
- kopírovanie repozitára bez licencie, najmä AI·HOT;
- vytváranie plných článkov ku každej položke. Väčšina udalostí potrebuje presnú krátku wire kartu; iba vybrané idú do research lane.

## Odporúčané poradie teardownu a stavby

1. **Natural20 + Heatwire + StackBrief:** zmapovať verejnú event kartu, radenie, API a source detail; proti tomu položiť Netopier `/events` contract.
2. **AI·HOT:** rozobrať inbox, feedback schema, policy versions, diff approval, usage/system admin a oddelenie factual summary od editor take.
3. **Particle + HuggingNews:** navrhnúť event detail: 5W, osoby, presné citáty, dokumenty, otázky, source roles a timeline.
4. **News Minimalist:** vytvoriť slovenský golden set pre `public_consequence` a `adam_relevance`, vrátane lokálnych nehôd, športu, agentúrnych prepisov a politického využitia udalosti.
5. **Beehive + NEWSCOPE:** navrhnúť bounded research case a eval informačnej rozmanitosti.
6. **Machine Herald:** navrhnúť immutable editorial/publish ledger; publikovanie ponechať za Adamovým explicitným schválením.

Frontend má vzniknúť až z tejto domény. Hotový dashboard template môže urýchliť kreslenie, ale produktové jednotky musia byť `event`, `curation decision`, `research case`, `evidence pack`, `Adam note` a `publication revision` — nie iba článkové karty.

## Dôkazové a licenčné hranice

- Produktové počty, presnosť, náklady a zákaznícke tvrdenia sú označené ako first-party, pokiaľ neboli nezávisle overené.
- Verejný web dokazuje pozorovaný povrch, nie neverejný model, prompt, SLA ani internú redakčnú prax.
- Natural20 nemá v nájdených verejných materiáloch otvorený source repozitár ani licenciu na kopírovanie implementácie.
- AI·HOT je public GitHub repo, ale bez zistenej licencie; jeho kód sa nesmie preberať. Myšlienky a nezávisle nanovo implementované workflow sa dajú použiť.
- Heatwire je MIT, no názov a wordmark sú výslovne vyhradené mimo kódovej licencie.
- StackBrief/AI News Ranker a AATF sú Apache-2.0; Beehive a Machine Herald MIT. Pred prevzatím konkrétneho súboru treba zachovať notice/copyright a overiť aktuálny stav licencie v danom commite.
- NEWSCOPE je výskumná publikácia. Implementácia podľa paperu a použitie prípadného companion kódu sú dve odlišné licenčné otázky; companion repo licencia v tomto reze nebola overená.

## Primárne zdroje

- Natural20: [About](https://natural20.com/about), [scoring methodology](https://natural20.com/how-scoring-works), [live site](https://natural20.com/), [public feed API](https://natural20.com/api/feed), [llms.txt](https://natural20.com/llms.txt), [sample cluster](https://natural20.com/c/ghxyzl), [sample coverage article](https://natural20.com/coverage/anthropic-rubicon-pentagon-maduro-safety-pledge), [newsletter surface](https://course.natural20.com/).
- Products: [HuggingNews About](https://huggingnews.com/about), [Particle launch](https://particle.news/blog/introducing-particle-the-news-organized), [Particle funding/publisher announcement](https://particle.news/blog/particle-raises-series-a-to-accelerate-development-of-ai-powered-news-app), [News Minimalist About](https://www.newsminimalist.com/about), [AI Newsnow About](https://ainewsnow.io/about).
- Autonomous/editorial: [AI·HOT repo](https://github.com/xingfanxia/newsroom), [AI·HOT editorial policy](https://github.com/xingfanxia/newsroom/blob/main/modules/feed/runtime/policy/skills/editorial.skill.md), [Machine Herald About](https://machineherald.io/about/), [Machine Herald repo](https://github.com/the-machine-herald/machineherald.io), [HeadlinesForge](https://headlinesforge.com/), [Mastheads](https://mastheads.app/features), [Beatwire](https://www.beatwire.ai/), [A47](https://a47media.com/).
- OSS/research: [Heatwire](https://github.com/NinjaCodeTurtle/heatwire), [StackBrief / AI News Ranker](https://github.com/AlexK020908/AI-News-Ranker), [AATF AI News Aggregator](https://github.com/flyryan/ai-news-aggregator), [Beehive](https://github.com/sinmentis/beehive), [NEWSCOPE paper](https://aclanthology.org/2025.emnlp-main.1722/).
