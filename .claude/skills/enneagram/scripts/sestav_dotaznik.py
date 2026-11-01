"""Generátor assets/dotaznik.json + assets/dotaznik.md. Výroky uprav zde a spusť: python3 scripts/sestav_dotaznik.py"""
import json, random, sys, pathlib

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent / "assets"

TYPY = {
1: ["Když vidím, že se něco dělá špatně, mám silnou potřebu to napravit.",
    "V hlavě mi často běží vnitřní kritik, který hodnotí, co dělám.",
    "Je pro mě těžké nechat práci „dost dobrou“, když vím, že by mohla být lepší.",
    "Zlost si většinou nedovolím ukázat; spíš se projeví jako podráždění nebo napětí v těle.",
    "Řídím se tím, co je správné, i když je to pro mě nevýhodné.",
    "Vadí mi, když druzí nedodržují pravidla nebo dohody.",
    "Odpočinek si často musím nejdřív „zasloužit“ splněním povinností.",
    "Chyby – své i cizí – si všimnu dřív než toho, co se povedlo.",
    "Mám jasnou představu o tom, jak by věci měly být.",
    "Cítím osobní odpovědnost za to, aby věci kolem mě byly v pořádku."],
2: ["Snadno vycítím, co druzí potřebují, často dřív než oni sami.",
    "Pomáhat druhým mi dává pocit, že mám své místo.",
    "Těžko říkám ne, když mě někdo požádá o pomoc.",
    "O vlastních potřebách se mi mluví těžko.",
    "Zabolí mě, když nikdo neocení, kolik pro druhé dělám.",
    "Blízké vztahy s lidmi jsou pro mě to nejdůležitější v životě.",
    "Umím se přizpůsobit tak, aby mě druzí měli rádi.",
    "Když moje péče zůstane bez odezvy, cítím křivdu.",
    "Lidé za mnou přirozeně chodí se svými starostmi.",
    "Je pro mě důležité, aby mě druzí potřebovali."],
3: ["Je pro mě důležité podávat výkon a dosahovat cílů.",
    "Rychle vycítím, co se v dané situaci oceňuje, a umím se tomu přizpůsobit.",
    "Záleží mi na tom, jakým dojmem působím.",
    "Pocity si často odkládám na později, aby mi nebránily v práci.",
    "Neúspěch beru velmi osobně, jako by vypovídal o mé hodnotě.",
    "Motivuje mě vidět měřitelný pokrok.",
    "Hledám nejefektivnější cestu k výsledku a nesnáším zdržování.",
    "Někdy nevím, kdo jsem bez svých výsledků a rolí.",
    "Uznání a obdiv mě silně motivují.",
    "Když něco dělám, chci v tom patřit mezi nejlepší."],
4: ["Často mám pocit, že mi chybí něco, co ostatní mají.",
    "Je pro mě zásadní žít v souladu s tím, kdo opravdu jsem.",
    "Prožívám emoce intenzivněji než většina lidí kolem mě.",
    "Přitahuje mě to, co je nedosažitelné nebo vzdálené.",
    "Vadí mi představa obyčejného, zaměnitelného života.",
    "Melancholie má pro mě zvláštní krásu.",
    "Často se srovnávám s druhými a vychází mi z toho, že jsem na tom hůř.",
    "Potřebuji, aby mě druzí opravdu pochopili, ne jen vyslechli.",
    "Přirozeně se vyjadřuji skrze estetiku, umění nebo osobní styl.",
    "V něčem zásadním se cítím odlišně od ostatních."],
5: ["Čas o samotě je pro mě nezbytný k obnovení energie.",
    "Než začnu jednat, chci věci do hloubky pochopit.",
    "Pečlivě si hlídám svůj čas, energii a soukromí.",
    "Emoce zpracovávám spíš později, v klidu, než v danou chvíli.",
    "Příliš mnoho požadavků od druhých mě rychle vyčerpá.",
    "Ve skupině spíš pozoruji, než se zapojuji.",
    "Chci mít v oblasti, která mě zajímá, skutečně hluboké znalosti.",
    "Vystačím si s málem, pokud mám klid a nezávislost.",
    "Vadí mi, když ode mě někdo čeká víc, než chci dát.",
    "Přemýšlení v soukromí mi vyhovuje víc než přemýšlení nahlas s ostatními."],
6: ["Často předvídám, co by se mohlo pokazit.",
    "Než se někomu svěřím, potřebuji si ověřit, že je důvěryhodný.",
    "Loajalita k lidem a skupinám, ke kterým patřím, je pro mě zásadní.",
    "Pochybuji o vlastních rozhodnutích a hledám potvrzení od ostatních.",
    "K autoritám mám dvojaký vztah: hledám u nich oporu, a zároveň jim nedůvěřuji.",
    "V krizi umím fungovat lépe, než by se dalo čekat.",
    "Mám ve zvyku mít připravený plán B.",
    "Když je něco až příliš dobré, hledám, kde je háček.",
    "Bezpečí a jistota jsou pro mě velmi důležité.",
    "Úzkost nebo vnitřní neklid jsou mými častými společníky."],
7: ["Mám v hlavě spoustu plánů a nápadů a těžko si mezi nimi vybírám.",
    "Když přijde nepříjemný pocit, rychle se přesunu k něčemu příjemnějšímu.",
    "Omezování a nuda jsou pro mě těžko snesitelné.",
    "Vidím v životě hlavně možnosti a příležitosti.",
    "Závazky mě znervózňují, protože zavírají jiné možnosti.",
    "Umím přerámovat problém tak, aby vypadal pozitivně.",
    "Rychle se nadchnu, ale stejně rychle přecházím k dalšímu.",
    "Chci toho v životě zažít co nejvíc.",
    "Když se mluví o bolesti, mám tendenci atmosféru odlehčit.",
    "Na budoucí zážitky se často těším víc, než prožívám ty současné."],
8: ["Říkám věci na rovinu, i když to druhé může zaskočit.",
    "Nesnesu, když mě někdo ovládá nebo mi diktuje, co mám dělat.",
    "Když nikdo nepřebírá vedení, rychle ho převezmu.",
    "Přiznat zranitelnost je pro mě těžké.",
    "Chráním lidi, na kterých mi záleží, a zastávám se slabších.",
    "Konflikt mi nevadí; v něm se ukáže, kdo je doopravdy zač.",
    "Respektuji lidi, kteří se mi umějí postavit.",
    "Mám hodně energie a jdu do věcí naplno.",
    "Nespravedlnost ve mně vyvolá okamžitou a silnou reakci.",
    "Nechci se spoléhat na druhé; raději mám věci pod kontrolou."],
9: ["Konflikty se snažím uklidnit nebo se jim vyhnout.",
    "Snadno vidím pohled všech zúčastněných stran.",
    "Často těžko poznávám, co doopravdy chci.",
    "Přizpůsobuji se přáním ostatních, aby byl klid.",
    "Důležité úkoly odkládám a věnuji se raději drobnostem nebo rutině.",
    "Lidé o mně říkají, že je se mnou pohoda.",
    "Vlastní zlost si dlouho neuvědomuji; pak se může projevit tvrdohlavostí.",
    "Pohodlí a příjemná rutina jsou pro mě důležité.",
    "Mám pocit, že na mém názoru tolik nezáleží.",
    "Dokážu se „ztratit“ v činnostech, které mě uklidňují (seriály, jídlo, koníčky)."],
}

INSTINKTY = {
"sp": ["Hlídám si zdraví, spánek, jídlo a finanční jistotu.",
       "Domov a pohodlné zázemí jsou pro mě prioritou.",
       "Často řeším, zda mám dostatek zdrojů – peněz, času, energie.",
       "Ve stresu nejdřív řeším praktické zajištění.",
       "Klidný večer doma je pro mě obvykle lepší než společenská akce.",
       "Plánuji dopředu, aby mi nic podstatného nechybělo."],
"so": ["Zajímá mě, jaké mám postavení ve skupině nebo komunitě.",
       "Sleduji, co se děje ve skupinách, kam patřím, a jaké jsou v nich vztahy.",
       "Je pro mě důležité přispívat něčím širšímu celku.",
       "Rychle vnímám nepsaná pravidla a hierarchii.",
       "Udržování široké sítě kontaktů je pro mě přirozené.",
       "Vyloučení z kolektivu je pro mě jedna z nejhorších věcí."],
"sx": ["Vyhledávám intenzivní spojení s jedním člověkem.",
       "Přitažlivost a chemie mezi lidmi je pro mě silný motor.",
       "Když mě něco nebo někdo zaujme, jdu do toho celou bytostí.",
       "Povrchní rozhovory mě nudí; chci jít do hloubky.",
       "Hodně vnímám, jak působím na lidi, kteří mě zajímají.",
       "Vztah bez jiskry je pro mě těžko snesitelný."],
}

RYCHLY = [
 {"id": "R1", "osa": "hornevian",
  "otazka": "Jak obvykle jdeš za tím, co chceš nebo potřebuješ?",
  "moznosti": [
   {"kod": "A", "skupina": "asertivni", "typy": [3, 7, 8],
    "text": "Jdu si za tím přímo. Jednám, prosazuji se, beru si prostor a očekávám, že se věci pohnou."},
   {"kod": "B", "skupina": "vyhovujici", "typy": [1, 2, 6],
    "text": "Snažím se dělat to, co je správné a co se ode mě čeká. Plním závazky a odpovědnost a věřím, že se mi to vrátí."},
   {"kod": "C", "skupina": "stazeni", "typy": [4, 5, 9],
    "text": "Nejdřív se stáhnu do sebe a věci zpracuji uvnitř. Potřebuji prostor a čas, než se zapojím."}]},
 {"id": "R2", "osa": "harmonicka",
  "otazka": "Jak obvykle reaguješ, když se něco pokazí nebo přijde konflikt?",
  "moznosti": [
   {"kod": "A", "skupina": "pozitivni", "typy": [2, 7, 9],
    "text": "Snažím se udržet dobrou náladu, vidět světlou stránku a nezatěžovat ostatní. Těžké pocity raději neřeším."},
   {"kod": "B", "skupina": "kompetencni", "typy": [1, 3, 5],
    "text": "Odložím emoce stranou a řeším problém věcně, logicky a efektivně. Pocity mohou počkat."},
   {"kod": "C", "skupina": "reaktivni", "typy": [4, 6, 8],
    "text": "Reaguji emočně a potřebuji, aby druzí moje pocity vzali vážně a reagovali, než se pohneme dál."}]},
]

SKALA = {"1": "vůbec neplatí", "2": "spíše neplatí", "3": "napůl", "4": "spíše platí", "5": "zcela platí"}

def main():
    rnd = random.Random(9)  # pevné pořadí
    # Část B: 90 výroků, promíchat tak, aby se typy střídaly
    polozky = []
    for kolo in range(10):
        poradi = list(TYPY)
        rnd.shuffle(poradi)
        if polozky and poradi[0] == polozky[-1]["typ"]:
            poradi.append(poradi.pop(0))
        for t in poradi:
            polozky.append({"typ": t, "text": TYPY[t][kolo]})
    for i, p in enumerate(polozky, 1):
        p["id"] = f"B{i:02d}"
    # Část C: 18 výroků o instinktech
    inst = []
    for kolo in range(6):
        poradi = list(INSTINKTY)
        rnd.shuffle(poradi)
        for k in poradi:
            inst.append({"instinkt": k, "text": INSTINKTY[k][kolo]})
    for i, p in enumerate(inst, 1):
        p["id"] = f"C{i:02d}"

    data = {
        "nazev": "Enneagram – orientační dotazník",
        "verze": "1.0",
        "jazyk": "cs",
        "poznamka": "Původní, nevalidovaný dotazník k sebereflexi. Nejde o diagnostiku.",
        "instrukce": ("Odpovídej podle toho, jak se chováš a prožíváš věci většinu života (zhruba od 20 let), "
                      "ne podle toho, jak bys chtěl/a být nebo jak je to zrovna teď. Nepřemýšlej příliš dlouho."),
        "skala": SKALA,
        "cast_a": RYCHLY,
        "cast_b": [{"id": p["id"], "typ": p["typ"], "text": p["text"]} for p in polozky],
        "cast_c": [{"id": p["id"], "instinkt": p["instinkt"], "text": p["text"]} for p in inst],
    }
    (OUT / "dotaznik.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    md = [f"# {data['nazev']}", "",
          f"> {data['poznamka']}", "",
          f"**Instrukce:** {data['instrukce']}", "",
          "Vyplnění trvá asi 15 minut. Odpovědi zapiš do hranatých závorek, nebo použij JSON šablonu "
          "(`python3 scripts/vyhodnot.py --sablona > odpovedi.json`) a vyhodnoť `python3 scripts/vyhodnot.py odpovedi.json`.", "",
          "## Část A – rychlý test (vyber vždy jednu možnost: A, B, nebo C)", ""]
    for q in RYCHLY:
        md.append(f"**{q['id']}. {q['otazka']}** &nbsp; Odpověď: [ ]")
        md.append("")
        for m in q["moznosti"]:
            md.append(f"- **{m['kod']}** – {m['text']}")
        md.append("")
    skala = " · ".join(f"{k} = {v}" for k, v in SKALA.items())
    md += ["## Část B – 90 výroků", "", f"Škála: {skala}", "",
           "| ID | Výrok | 1–5 |", "|---|---|---|"]
    md += [f"| {p['id']} | {p['text']} | [ ] |" for p in polozky]
    md += ["", "## Část C – 18 výroků o instinktech", "", f"Škála: {skala}", "",
           "| ID | Výrok | 1–5 |", "|---|---|---|"]
    md += [f"| {p['id']} | {p['text']} | [ ] |" for p in inst]
    md += ["", "---", "_Klíč k vyhodnocení je v `dotaznik.json`; ruční vyhodnocení: průměr 10 výroků každého typu (část B) "
           "a 6 výroků každého instinktu (část C)._", ""]
    (OUT / "dotaznik.md").write_text("\n".join(md), encoding="utf-8")

    # Vložit data do webové aplikace (enneagram/index.html v kořeni repozitáře), pokud existuje.
    app = pathlib.Path(__file__).resolve().parents[4] / "enneagram" / "index.html"
    if app.exists():
        import re
        html = app.read_text(encoding="utf-8")
        kompakt = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        html, n = re.subn(r"/\*DATA\*/.*?/\*/DATA\*/", lambda m: f"/*DATA*/{kompakt}/*/DATA*/", html, flags=re.S)
        if n == 1:
            app.write_text(html, encoding="utf-8")
            print(f"Data vložena do {app}")

main()
