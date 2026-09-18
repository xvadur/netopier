# Globálne verejné inštitucionálne dáta pre Netopier

**Dátum prieskumu:** 5. september 2026  
**Stav:** dokumentácia overená; žiaden z nižšie uvedených zdrojov ešte neprešiel integračnou vzorkou ani pravidelným zberom v Netopieri.

## Účel a hranica

Tieto zdroje nie sú náhradou za primárny záznam konkrétneho slovenského prípadu (uznesenie, zmluva, výrok alebo register). Tvoria medzinárodnú kontextovú vrstvu: k tvrdeniu alebo udalosti dodajú dohľadateľnú časovú radu, metodiku, porovnanie štátov alebo svetové mediálne pokrytie. Pred automatickým použitím treba pre každý vybraný dataset overiť vzorku, licenciu a aktualizačný režim.

## Kandidáti s dokumentovaným strojovým prístupom

| Zdroj | Čo dáva | Prístup a výstup | Identita, história a prevádzkové podmienky | Stav / úloha pre Netopier |
| --- | --- | --- | --- | --- |
| **World Bank Indicators API v2** | Takmer 16 000 indikátorových časových radov z viac než 45 databáz, vrátane WDI a International Debt Statistics. | Verejné REST API `https://api.worldbank.org/v2/`; XML, JSON a JSONP. Príklad: `country/SVK/indicator/NY.GDP.MKTP.CD?format=json`. Oficiálny export umožňuje CSV/XML/XLSX v ZIP. | Reprodukovateľná séria je kombinácia krajiny/agregátu, kódu indikátora a obdobia; Slovensko používa `SVK`. V2 nahradila ukončené V1. Autentifikácia ani API kľúč sa nevyžadujú. Dokumentácia uvádza štandardných 50 položiek na stránku, maximum 60 indikátorov v multi-indicator požiadavke a limit 4 000 znakov URL; pre WDI SDMX je limit 15 000 datapointov vrátane nullov na požiadavku. | **Dokumentácia overená.** Dobrá vrstva pre kontrolu trendu a medzinárodné porovnanie, nie pre real-time eventy. Prvý test: jedna séria pre `SVK`, metadata indikátora, metóda a stránkovanie. |
| **OECD Data Explorer** | Medzinárodné série z ekonomiky, verejných financií, práce, vzdelávania, obchodu, životného prostredia a správy vecí verejných. | Verejné SDMX REST API `https://sdmx.oecd.org/public/rest/`; dátové, štruktúrne a availability dopyty. Výstupy XML, JSON, CSV a CSV s kódmi i popismi. Zoznam dataflowov: `.../dataflow/all`. | Identita pozorovania: agency ID + dataflow/dataset + verzia + dimenzionálny kľúč + čas. API je bezplatné pri prijatí podmienok OECD. OECD výslovne uvádza rate limiting, ale v nájdenej dokumentácii nepublikuje číselný limit; odporúča cache, content-constraint a malé filtrované dopyty. Väčšina datasetov sa mení zriedka, revízie bývajú často raz alebo dvakrát ročne. | **Dokumentácia overená.** Vhodný pre porovnateľné súvislosti, najmä keď sa musí uchovať aj dátová štruktúra a verzia. Prvý test: dataflow, codelist, `contentconstraint`, úzky CSV výrez. |
| **IMF Data / SDMX** | Makroekonomické, menové, platobnobilančné, fiškálne a finančné dáta IMF. | IMF uvádza rozhrania SDMX 2.1 a 3.0; dokumentácia smeruje na API postupy pre Python, R, Stata a MATLAB. Samostatný IMF SDMX Central má web-service guide a vstup `https://sdmxcentral.imf.org/sdmx/v2/`. | SDMX identita je dataflow/dataset, dimenzie, codelisty, frekvencia a časový rozsah. Aktuálna oficiálna stránka pri hlavnom API uvádza exploráciu Swaggeru po prihlásení beta-portal účtom; preto bez reálnej skúšky netvrdiť bezautentifikačný produkčný prístup. Numerický rate limit ani licencia neboli v použitých technických podkladoch zistené. | **Dokumentácia overená, prístupový režim otvorený.** Kandidát na manuálne/periodické makro overenie; pred konektorom treba založiť alebo použiť povolený účet a uchovať odpoveď s metadátami. |
| **UN Statistics Division: UNdata a Global SDG Database** | UNdata obsahuje štatistické datamarty; Global SDG Database dáva globálne indikátory SDG a ich metodické metadáta. | UNdata: SDMX REST `http://data.un.org/ws/rest/` aj SOAP; XML, JSON a CSV. SDG: Swagger `https://unstats.un.org/SDGAPI/swagger/`, SDMX API a dataflow `DF_SDG_GLH`; samostatné metadata API. | Pri SDG je identita séria/indikátor, geografická oblasť, dimenzie disaggregácie a čas. Geografická schéma používa M49 číselné kódy, teda nie automaticky ISO `SVK`. UNSD uvádza plánované hlavné aktualizácie približne marec/apríl, jún/júl, september a december; staršie verzie databázy sú dostupné. Dokumentácia neuvádza jasný číselný rate limit. UNdata výslovne upozorňuje, že SDMX API nie je dostupné pre každý datamart, len tam, kde existuje DSD. | **Dokumentácia overená.** Pre ukazovatele SDG uchovať dataflow, dimenzie, M49, vydanie databázy a odkaz na metodiku; zdroj používať ako kontext k tvrdeniu, nie samostatný dôkaz príčiny. |
| **GDELT Project** *(medzinárodný verejný dátový projekt, nie štátny ani medzivládny register)* | Priebežný globálny index a extrakcie z online správ: udalosti, mentions, entity, témy, lokácie, citáty a front pages. | Verejné hromadné downloady a živé JSON API (DOC, GEO, TV); GDELT uvádza plnotextové vyhľadávanie. | GDELT 2.0 event a GKG vrstvy aktualizuje každých 15 minút a obsahuje 65 strojovo prekladaných jazykov. Frontpage Graph skenuje homepages 50 000 médií každú hodinu; Global Difference Graph kontroluje články po 24 hodinách a týždni kvôli zmenám. V niektorých produktoch je explicitne uvedený alpha/experimentálny stav. V použitej dokumentácii nebol jasný číselný rate limit ani licencia. | **Dokumentácia overená.** Vhodné len ako discovery a mediálny signál; každý relevantný nález musí viesť späť na pôvodný článok a pri verejnom tvrdení na primárny dokument. Prvý test: úzky DOC dotaz, archivácia URL/času a porovnanie s vlastnými RSS zdrojmi. |

## Spoločný kontrakt pre budúci konektor

Pre medzinárodný štatistický záznam nestačí uložiť hodnotu. Každý import musí mať minimálne:

```text
institution
source_or_dataflow_id
series_or_indicator_code
geography_scheme_and_code
dimensions
time_period
value_and_unit
retrieved_at
release_or_dataset_version
source_url
methodology_or_metadata_url
raw_payload_hash
```

Globálny mediálny signál má navyše jasne označiť, že nejde o primárny záznam udalosti, a zachovať `source_url`, čas záznamu, kolekčný čas, identifikátor GDELT záznamu, dotaz a raw payload hash.

## Odporúčané poradie praktického overenia

1. **World Bank**: malá séria pre Slovensko a dve porovnávacie krajiny; overiť metadáta, stránkovanie, časové medzery a revision-safe ukladanie.
2. **OECD**: jeden úzky dataflow so štruktúrou, codelistom a `contentconstraint`; overiť identitu série aj dostupnosť verzie.
3. **UN SDG**: jedna séria s M49, disaggregáciami a metodikou; overiť rozdiel medzi dátom publikovania, pozorovaním a revíziou.
4. **GDELT**: iba obmedzený discovery experiment; zmerať prekryv, oneskorenie a falošné zhody proti vlastným zdrojom.
5. **IMF**: až po overení autorizácie/účtu a reálneho malého exportu.

## Primárne zdroje

- World Bank: [Indicators API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation), [basic call structure](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures), [SDMX API query limits](https://datahelpdesk.worldbank.org/knowledgebase/articles/1886701-sdmx-api-queries).
- OECD: [Data via API](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html), [API best practices](https://www.oecd.org/en/data/insights/data-explainers/2024/11/Api-best-practices-and-recommendations.html), [SDMX Swagger](https://sdmx.oecd.org/public/swagger/index.html?urls.primaryName=v2).
- IMF: [IMF API](https://data.imf.org/en/Resource-Pages/IMF-API), [IMF SDMX Central web-service guide](https://dsbb.imf.org/content/pdfs/IMFSDMXCentralWebServicesGuide.pdf).
- United Nations: [UNdata API manual](https://data.un.org/Host.aspx?Content=API), [UNSD API catalogue](https://unstats.un.org/unsd/api/), [SDG API Swagger](https://unstats.un.org/SDGAPI/swagger/), [SDMX-SDG API manual](https://unstats.un.org/sdgs/files/SDMX_SDG_API_MANUAL.pdf), [SDG Database](https://unstats.un.org/sdgs/dataportal/database).
- GDELT: [Data and APIs](https://www.gdeltproject.org/data.html).
