# postobot
<span>

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)  ![](https://github.com/rcastellotti/postobot/actions/workflows/main.yml/badge.svg) ![](https://img.shields.io/docker/pulls/rcastellotti/postobot.svg)

</span>

## Configurazione
+ Crea un bot su Telegram con [BotFather](https://t.me/botfather)
+ Configura la variabile d'ambiente `BOT_TOKEN` il token che ti ha dato BotFather
+ \[Opzionale\]: Configura i comandi del bot con `/mybots -> scegli il tuo bot -> edit bot -> edit commands`:
  ```
  start - Avvia il bot e stampa il messaggio principale
  prenota - Prenota una lezione tra quelle disponibili
  prenotate - Ottieni il QR di una lezione tra quelle prenotate
  cancella - Cancella una lezione tra quelle prenotate
  annulla - Annulla la procedura corrente
  ```
+ \[Opzionale\]:Configura la bot description con `/mybots -> scegli il tuo bot -> edit bot -> edit description`:
  ```
  Questo bot permette di prenotare i posti a lezione per i corsi di UniGe.
  /prenota prenota una lezione tra quelle disponibili.
  /prenotate ottieni il QR di una lezione tra quelle prenotate.
  /cancella cancella una lezione tra quelle prenotate.
  /annulla annulla la procedura corrente.
  ```
+ \[Opzionale\]: per maggiore sicurezza puoi settare il bot in modo che i comandi siano usabili solo da te, per farlo e' sufficiente settare la variabile di ambiente `CHAT_ID`, puoi ottenerlo contattando [IDBot](http://t.me/myidbot).

## Deployment

### Deploy tradizionale (raccomandato)

Esempio di  `docker-compose.yml`
```yml
version: "3.1"
services:
  db:
    image: postgres:alpine
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_DB: postobot
      POSTGRES_PASSWORD: <POSTGRES_PASSWORD>

  bot:
    image: rcastellotti/postobot:latest
    environment:
      BOT_TOKEN: <BOT_TOKEN>
      CHAT_ID: <CHAT_ID>
      DATABASE_URL: postgresql+psycopg2://postgres:<POSTGRES_PASSWORD>@db/postobot
      GECKODRIVER_PATH: /usr/bin/geckodriver
      MATRICOLA: <MATRICOLA>
      PASSWORD: <PASSWORD>
```

### Deploy su Heroku

Puoi deployare e configurare `postobot` su [Heroku](https://heroku.com) usando questo button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rcastellotti/postobot/tree/heroku)

### Technical Stuff

La variabile d' ambiente `GECKODRIVER_PATH` e' necessaria per utilizzare il [buildpack](https://devcenter.heroku.com/articles/buildpacks) [heroku-integrated-firefox-geckodriver](https://elements.heroku.com/buildpacks/pyronlaboratory/heroku-integrated-firefox-geckodriver)

La Github Action [`heroku.yml`](https://github.com/rcastellotti/postobot/blob/main/.github/workflows/heroku.yml) aggiorna ad ogni commit il [subtree](https://www.atlassian.com/git/tutorials/git-subtree) [heroku](https://github.com/rcastellotti/postobot/tree/heroku) necessario per un funzionamento corretto di Heroku (`app.json`,`Procfile` e `requirements.txt` devono necessariamente essere nella basedir).

La Github Action [`main.yml`](https://github.com/rcastellotti/postobot/blob/main/.github/workflows/main.yml) builda l' immagine docker e la pusha in automatico su [DockerHub](https://hub.docker.com/rcastellotti/postobot).

Dal momento che il bot per funzionare ha bisogno di matricola e password in chiaro (devono essere inserite da [Selenium](https://selenium.dev) ) abbiamo deciso di non hostarne uno e dare la possibilita' di registrarsi per garantire maggiore privacy e sicurezza, deployare il bot dovrebbe essere un processo semplice, in caso di problemi  apri un issue e proveremo ad aiutarti.


## Altri atenei

Non dovrebbe essere complesso adattare questo bot a qualsiasi ateneo che usi [EasyAcademy](https://www.zucchetti.it/website/cms/prodotto/2969-gestione-appelli-desame-e-orari-lezioni-universita.html), e' necessario tuttavia modificare gli URL e le funzioni per l' autenticazione (probabilmente SSO).



## Autori

- [Fabio Fontana](https://fabifont.github.io)
- [Roberto Castellotti](https://rcastellotti.dev)
