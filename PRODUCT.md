# Netopier — produktový kontext

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Slovensky čítajúci návštevník, ktorý chce pochopiť verejné udalosti, ich vývoj,
zdroje a rozdiely v pokrytí. Presný cieľový segment zostáva otvorený.
Pri tejto explorácii je hodnotiteľom Adam; ráno vyberá zo širokej palety návrhov.

## Product Purpose

Netopier má poskytovať stručné, zdrojovo ohraničené správy o udalostiach.
Produktová hypotéza a zodpovednosť za publikáciu sú v docs/PRODUCT_HYPOTHESIS.md.
Zadanie z 9. septembra 2026: výskum spravodajských produktov a približne 50
odvážnych lokálnych frontendových prototypov na ranný výber. Adam výslovne
potvrdil široký záber aj radikálne odlišné podoby. Následne vybral prvý koncept
Vydanie a požiadal rozvinúť práve ten. Aktuálne zadanie je funkčný frontend
tohto smeru; výroba päťdesiatich webov sa ďalej nevykonáva.

## Positioning

Vstupnou jednotkou je udalosť s vývojom a odkazmi na zdroje. Dizajn má umožniť
rýchle čítanie aj overenie pôvodu. Ambícia prekonať slovenské redakčné weby
je cieľom, nie overeným výsledkom či verejným marketingovým tvrdením.

## Operating Context

Lokálna galéria umožní porovnávanie návrhov na tom istom obsahu, výber favoritov
a otvorenie funkčných prototypov. Súčasný backend a jeho dáta sa nemenia.
README zo 7. septembra zaznamenáva odstavený kontajnerový runtime.

## Capabilities and Constraints

V2 obsahuje MinifluxGateway, ArticleArchive, StoryEngine a FeedProjector.
Frontendové prototypy sú samostatnou lokálnou exploráciou, bez tvrdenia o živom
zbere, publikácii, redakčnom overení alebo napojení na produkciu. Ukážkový obsah
musí byť označený. Nové schopnosti porovnávania a vizualizácie sú návrhy.
Bez pushu, deployu, publikácie, nového trvalého servisu a obnovy v0.

## Brand Commitments

Názov Netopier, slovenský jazyk. Odvážny, krásny, moderný spravodajský produkt.
Ground News a Minúta po minúte sú explicitné referencie na výskum a porovnanie.
Vybraný prvý koncept uzamyká veľký NETOPIER, serifovú typografiu, pravú bielu,
čierny text, červené akcenty a novinové stĺpce. Podrobnosti vlastní DESIGN.md.

## Evidence on Hand

docs/PRODUCT_HYPOTHESIS.md, docs/ARCHITECTURE.md, contracts/feed.example.json,
contracts/story.example.json. Príklady kontraktov predstavujú starší snapshot,
nie dnešné správy. Všetky simulované údaje explorácie musia byť zreteľné.

## Product Principles

- Pôvod informácie musí zostať prístupný pri čítaní.
- Udalosť, zdroj, interpretácia a neistota zostávajú rozlíšené.
- Návrhy sa porovnávajú na rovnakom obsahovom základe.
- Vizuálna rozmanitosť potrebuje rozdielnu kompozíciu a spôsob čítania.
- Finálny vkus a výber patria Adamovi.
