Tato aplikace využívá otevřená data Český hydrometeorologický ústav k zobrazení všech dostupných textových předpovědí počasí v jednoduchém, tradičním stylu.

Obsahuje předpovědi pro jednotlivé kraje, celou Českou republiku i vybraná pohoří.

Všechny předpovědi jsou psány lidskými meteorology a nejsou automaticky generovány z numerických modelů.

Hlavní soubor pro spuštění aplikace je streamlit_web_page_005.py.
Funkční webová aplikace (vytvořená pomocí Streamlit) je dostupná zde: https://zobrazeni-predpovedi-r9c7dyy8wx8nzhrfsmoznf.streamlit.app/
Lepší rozšířená aplikace obsahující i možnost zobrazit grafy všech dostupných meteo stanic je zde: https://meteo-open-data-chmu.streamlit.app/

Aplikaci může při otevření trvat několik sekund, než se načte, zejména pokud byla delší dobu neaktivní je potřeba ji probudit kliknutím na modré tlačítko.
To je běžné chování — aplikace se při nečinnosti automaticky uspí a při dalším otevření potřebuje krátký čas na opětovné spuštění.


This app uses open data from the Czech Hydrometeorological Institute to display all available text weather forecasts in a simple, classic style.

It includes forecasts for individual regions, the entire Czech Republic, and selected mountain ranges.

All forecasts are written by human meteorologists and are not automatically generated from weather models.

The main file to run the app is streamlit_web_page_005.py.
A live version of the web application (built with Streamlit) is available here: https://zobrazeni-predpovedi-r9c7dyy8wx8nzhrfsmoznf.streamlit.app/
Better (extended) application including also the option to show graphs from all the available meteorological stations is here: https://meteo-open-data-chmu.streamlit.app/

The app may take a few seconds to load when you open it, especially if it has been inactive for a while (click of the button brings it back up).
This is normal behavior — the app automatically goes to sleep when not in use and needs a short moment to start again.
