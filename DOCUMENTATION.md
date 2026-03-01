# PhotoAlbum – Projekt dokumentáció

## 1. Áttekintés

A PhotoAlbum egy felhő alapú webalkalmazás, amelyben a felhasználók fényképeket tölthetnek fel, böngészhetnek és törölhetnek. Az alkalmazás egy PaaS (Platform as a Service) környezetben fut, és egy skálázható, többrétegű architektúrát valósít meg.

Az alkalmazás **Django** (Python) webes keretrendszerrel készült, **Heroku**-n van üzemeltetve, képtárolásra **Cloudinary**-t, adatbázisként pedig **Heroku PostgreSQL**-t használ.

---

## 2. Funkcionális követelmények

Az alkalmazás az alábbi funkciókat valósítja meg:

- **Feltöltés és törlés** – bejelentkezett felhasználók képeket tölthetnek fel és törölhetik a sajátjaikat.
- **Metaadatok** – minden képnek van neve (max. 40 karakter) és automatikusan rögzített feltöltési dátuma (formátum: ÉÉÉÉ-HH-NN ÓÓ:PP).
- **Listázás és rendezés** – az összes kép listázható, név (A→Z, Z→A) vagy dátum (legújabb/legrégebbi) szerint rendezve. Névre is lehet szűrni.
- **Részletes nézet** – a listában egy képre kattintva megjelenik a teljes méretű kép a metaadatokkal együtt.
- **Felhasználókezelés** – regisztráció, belépés és kilépés lehetséges.
- **Hozzáférés-szabályozás** – feltöltni és törölni csak bejelentkezett felhasználó tud, és egy képet csak a feltöltője vagy egy adminisztrátor törölhet.

---

## 3. Technológiai stack

| Komponens | Technológia |
|---|---|
| Programozási nyelv | Python 3 |
| Webes keretrendszer | Django 4.2 |
| Alkalmazásszerver | Gunicorn |
| PaaS platform | Heroku |
| Produkciós adatbázis | Heroku PostgreSQL (essential-0) |
| Képtároló | Cloudinary |
| Statikus fájlok kiszolgálása | WhiteNoise |
| Környezeti konfiguráció | python-decouple |
| Frontend | Bootstrap 5, Bootstrap Icons |

---

## 4. Architektúra

Az alkalmazás klasszikus **háromrétegű architektúrát** követ, amely lehetővé teszi a vízszintes skálázást Heroku-n:

```
┌─────────────┐        HTTPS         ┌──────────────────────────────┐
│   Böngésző  │ ◄──────────────────► │  Heroku Dyno                 │
└─────────────┘                      │  Gunicorn + Django (app tier) │
                                     └──────────┬───────────┬────────┘
                                                │           │
                                    ┌───────────▼──┐  ┌─────▼──────────┐
                                    │  Heroku      │  │  Cloudinary    │
                                    │  PostgreSQL  │  │  CDN           │
                                    │  (data tier) │  │  (media tier)  │
                                    └──────────────┘  └────────────────┘
```

### Rétegek leírása

**Megjelenítési réteg** – A böngésző a Django sablon motor által szerver oldalon generált HTML oldalakat jeleníti meg. A stílusozáshoz Bootstrap 5-öt használ az alkalmazás. A statikus fájlokat (CSS) a WhiteNoise szolgálja ki közvetlenül a Gunicorn folyamatból.

**Alkalmazás réteg** – A Django a Gunicorn alkalmazásszerveren fut. Kezeli az összes HTTP kérést, elvégzi az üzleti logikát (hitelesítés, hozzáférés-ellenőrzés, rendezés, keresés), és kommunikál az adatbázissal és a képtárolóval. A Heroku-n futtatva a dynók száma kód módosítása nélkül növelhető.

**Adat réteg** – Két külön tárolórendszer van:
- **Heroku PostgreSQL** tárolja a relációs adatokat: felhasználók, képrekordok (név, dátum, tulajdonos).
- **Cloudinary** tárolja a tényleges képfájlokat. Ez azért szükséges, mert a Heroku dyno fájlrendszere ideiglenes – minden lokálisan írt fájl elvész újraindításkor vagy újratelepítéskor.

---

## 5. Projektstruktúra

```
.
├── photoalbum/               # Django projekt csomag (konfiguráció)
│   ├── settings.py           # Beállítások; környezeti változókból olvas
│   ├── urls.py               # Gyökér URL útvonalak
│   └── wsgi.py               # WSGI belépési pont a Gunicorn számára
│
├── photos/                   # Fő Django alkalmazás
│   ├── models.py             # Photo adatmodell
│   ├── views.py              # Nézet függvények (lista, részlet, feltöltés, törlés, regisztráció)
│   ├── forms.py              # PhotoUploadForm, RegisterForm
│   ├── urls.py               # Alkalmazásszintű URL minták
│   ├── admin.py              # Django admin konfiguráció
│   └── migrations/           # Adatbázis migrációs fájlok
│
├── templates/                # HTML sablonok (Django template nyelv)
│   ├── base.html             # Alap elrendezés: navigáció, üzenetek, lábléc
│   ├── registration/         # login.html, register.html
│   └── photos/               # list.html, detail.html, upload.html, delete_confirm.html
│
├── static/css/style.css      # Egyedi CSS stílusok
│
├── manage.py                 # Django parancssori eszköz
├── requirements.txt          # Python függőségek
├── Procfile                  # Heroku folyamatdefiníciók
├── runtime.txt               # Python verzió rögzítése Heroku számára
├── .env.example              # Környezeti változók sablonja
└── .gitignore
```

---

## 6. Adatmodell

Az alkalmazás a Django beépített `User` modelljét használja hitelesítéshez, és egy egyedi modellt definiál:

### `Photo`

| Mező | Típus | Leírás |
|---|---|---|
| `id` | BigAutoField (PK) | Automatikusan generált elsődleges kulcs |
| `name` | CharField (max 40) | A felhasználó által megadott képnév |
| `image` | ImageField | Hivatkozás a feltöltött képfájlra (Cloudinary-n tárolva) |
| `upload_date` | DateTimeField (auto) | Automatikusan kitöltött feltöltési időbélyeg |
| `owner` | ForeignKey → User | A képet feltöltő felhasználó |

---

## 7. Alkalmazáslogika

### URL útvonalak

| URL | Nézet | Hozzáférés |
|---|---|---|
| `/` | `photo_list` | Publikus |
| `/photo/<id>/` | `photo_detail` | Publikus |
| `/upload/` | `photo_upload` | Bejelentkezés szükséges |
| `/delete/<id>/` | `photo_delete` | Bejelentkezés + tulajdonos/admin |
| `/accounts/register/` | `register` | Publikus |
| `/accounts/login/` | `login` (beépített) | Publikus |
| `/accounts/logout/` | `logout` (beépített) | Csak POST |

### Hitelesítés és hozzáférés-szabályozás

A Django beépített `django.contrib.auth` rendszere kezeli a munkamenet alapú hitelesítést. A `@login_required` dekorátor a nem bejelentkezett felhasználókat a belépési oldalra irányítja. A `photo_delete` nézetben egy tulajdonosi ellenőrzés gondoskodik arról, hogy csak a kép feltöltője vagy egy adminisztrátor törölhessen.

### Konfiguráció kezelése

Minden érzékeny és környezetfüggő érték (titkos kulcs, adatbázis URL, Cloudinary hitelesítő adatok, debug jelző, engedélyezett hosztek) környezeti változóként van tárolva, és nem kerül be a verziókezelőbe. A `python-decouple` könyvtár lokálisan a `.env` fájlból, Heroku-n pedig a Config Vars-ból olvassa ezeket.

---

## 8. Telepítés

### Helyi fejlesztés

Lokálisan SQLite adatbázist és helyi fájlrendszert használ az alkalmazás. Egy `.env` fájl biztosítja a szükséges konfigurációt. A fejlesztői szerver indítása:

```bash
python manage.py runserver
```

### Heroku

A Heroku deployment a GitHub repozitorihoz van kapcsolva. Minden `main` ágra történő push automatikusan új buildet és deploymentet indít el. A `Procfile` két folyamattípust definiál:

```
release: python manage.py migrate --no-input && python manage.py collectstatic --no-input --clear
web:     gunicorn photoalbum.wsgi --log-file -
```

A `release` folyamat minden új verzió élesítése előtt lefut: elvégzi az adatbázis migrációkat és összegyűjti a statikus fájlokat. A `web` folyamat elindítja a Gunicorn alkalmazásszervert.

A biztonsági beállítások (HTTPS átirányítás, HSTS, secure sütik) automatikusan aktiválódnak, ha `DEBUG=False`.

---

## 9. Skálázhatóság

Az alkalmazás vízszintesen skálázható. Mivel minden állapot külső rendszerekben van tárolva (PostgreSQL az adatoknak, Cloudinary a képeknek), tetszőleges számú azonos Heroku dyno tudja kiszolgálni a kéréseket kódmódosítás nélkül. A skálázás egyetlen paranccsal elvégezhető:

```bash
heroku ps:scale web=3
```

A WhiteNoise az induláskor tömöríti és gyorsítótárazza a statikus fájlokat, így azok kiszolgálása nem jelent többletterhelést a dynók számának növelésekor.
