# Forglass Regenerator Optimizer - Instrukcja Użytkownika

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Logowanie](#logowanie)
3. [Dashboard - Przegląd](#dashboard)
4. [Konfiguracje Regeneratorów](#konfiguracje-regeneratorów)
5. [Scenariusze Optymalizacji](#scenariusze-optymalizacji)
6. [Uruchamianie Optymalizacji](#uruchamianie-optymalizacji)
7. [Monitorowanie Postępów](#monitorowanie-postępów)
8. [Przeglądanie Wyników](#przeglądanie-wyników)
9. [Baza Materiałów](#baza-materiałów)
10. [Raporty](#raporty)
11. [Rozwiązywanie Problemów](#rozwiązywanie-problemów)

---

## Wprowadzenie

**Forglass Regenerator Optimizer (FRO)** to zaawansowany system do optymalizacji regeneratorów pieców szklarskich, który umożliwia:

- 🔥 **Redukcję zużycia paliwa o 5-15%**
- 🌱 **Obniżenie emisji CO₂ o 5-15%**
- 💰 **Oszczędności energetyczne** do 357 000 USD rocznie
- 📊 **Symulacje termodynamiczne** w czasie rzeczywistym
- 🎯 **Optymalizację geometrii** regeneratorów metodą SLSQP

### Wymagania systemowe

- Przeglądarka: Chrome 90+, Firefox 88+, Edge 90+
- Rozdzielczość: minimum 1366x768
- Połączenie internetowe: stabilne (do synchronizacji danych)

---

## Logowanie

### Pierwsze logowanie

1. Otwórz przeglądarkę i wejdź na adres: **http://localhost:3000**
2. Wprowadź dane logowania:
   - **Użytkownik**: `admin`
   - **Hasło**: `admin`
3. Kliknij **"Zaloguj"**

### Poziomy dostępu

System obsługuje trzy role użytkowników:

| Rola | Uprawnienia |
|------|-------------|
| **ADMIN** | Pełny dostęp, zarządzanie użytkownikami, wszystkie funkcje |
| **ENGINEER** | Tworzenie i uruchamianie optymalizacji, przeglądanie wyników |
| **VIEWER** | Tylko podgląd wyników, bez możliwości edycji |

⚠️ **Ważne**: Po pierwszym logowaniu zmień hasło administratora!

---

## Dashboard - Przegląd

Dashboard to centrum kontrolne aplikacji, które wyświetla:

### Metryki w czasie rzeczywistym

- **Aktywne optymalizacje** - liczba obecnie działających zadań
- **Ukończone dzisiaj** - zadania zakończone w ciągu ostatnich 24h
- **Średnia efektywność** - uśredniona efektywność termiczna z ostatnich 7 dni
- **Oszczędności CO₂** - łączna redukcja emisji (kg/rok)

### Wykresy i trendy

- **Wykres efektywności w czasie** - trend poprawy wydajności
- **Porównanie konfiguracji** - baseline vs. optymalizowane wartości
- **Status systemów** - zdrowotność serwisów (Backend, Celery, Redis, MySQL)

### Szybkie akcje

- 🚀 **Nowa optymalizacja** - szybki start nowego zadania
- 📊 **Ostatnie wyniki** - podgląd najnowszych rezultatów
- 📈 **Raporty** - generowanie raportów PDF/Excel

---

## Konfiguracje Regeneratorów

### Tworzenie nowej konfiguracji

1. Przejdź do **"Konfiguracje"** w menu głównym
2. Kliknij **"Nowa Konfiguracja"**
3. Wypełnij formularz:

#### Geometria
- **Wysokość checkera** (1.0 - 3.0 m) - wysokość warstwowa materiału ogniotrwałego
- **Grubość ścianki** (0.1 - 1.0 m) - grubość ścian kanałów
- **Rozstaw checkerów** (0.03 - 0.15 m) - odstęp między elementami

#### Parametry termiczne
- **Temperatura wlotu spalin** (800 - 1700°C)
- **Temperatura wylotu spalin** (300 - 800°C)
- **Przepływ masy spalin** (5 - 100 kg/s)

#### Materiały
- **Materiał checkera** - wybierz z bazy (np. Silica Brick, Magnesia)
- **Materiał izolacji** - wybierz materiał izolacyjny

4. Kliknij **"Zapisz konfigurację"**

### Walidacja danych

System automatycznie sprawdza:
- ✅ Poprawność zakresów wartości
- ✅ Spójność fizyczną parametrów
- ✅ Dostępność materiałów w bazie
- ✅ Bilans cieplny

❌ **Błędy walidacji** - czerwone komunikaty pod polami z błędami
⚠️ **Ostrzeżenia** - żółte komunikaty sugerujące poprawki

---

## Scenariusze Optymalizacji

### Czym jest scenariusz?

**Scenariusz optymalizacji** to zestaw parametrów definiujących:
- Konfigurację bazową (punkt startowy)
- Cel optymalizacji (np. minimalizacja zużycia paliwa)
- Zmienne projektowe (co optymalizować)
- Algorytm (SLSQP, genetic algorithm)
- Ograniczenia (bounds, constraints)

### Tworzenie scenariusza

1. Przejdź do **"Optymalizacja" → zakładka "Scenariusze"**
2. Kliknij **"Nowy Scenariusz"**
3. Wypełnij dane:

#### Podstawowe informacje
- **Nazwa scenariusza** - opisowa nazwa (np. "Optymalizacja Piece #3")
- **Opis** - szczegóły problemu optymalizacyjnego
- **Konfiguracja bazowa** - wybierz istniejącą konfigurację

#### Cel optymalizacji
- 🔥 **Minimalizacja zużycia paliwa** (domyślnie)
- 🌱 **Minimalizacja emisji CO₂**
- 📈 **Maksymalizacja efektywności termicznej**
- ⚖️ **Wielokryterialna** (połączenie powyższych)

#### Algorytm
- **SLSQP** - Sequential Least Squares Programming (zalecane)
  - Szybki, precyzyjny, deterministyczny
  - Najlepszy dla problemów ciągłych z gradientem
- **PSO** - Particle Swarm Optimization (w przygotowaniu)
- **Genetic Algorithm** (w przygotowaniu)

#### Zmienne projektowe

Zaznacz parametry do optymalizacji:

| Zmienna | Zakres | Wpływ |
|---------|--------|-------|
| Wysokość checkera | 0.5 - 3.0 m | Czas kontaktu, powierzchnia wymiany |
| Grubość ścianki | 0.1 - 1.0 m | Straty ciepła, wytrzymałość |
| Rozstaw checkerów | 0.03 - 0.15 m | Opory przepływu, efektywność |

#### Parametry algorytmu
- **Max iteracji** (10 - 1000) - limit obliczeń (domyślnie: 100)
- **Tolerancja** (0.0001 - 0.1) - dokładność zbieżności (domyślnie: 0.001)
- **Timeout** (60 - 7200 s) - maksymalny czas wykonania

4. Kliknij **"Utwórz scenariusz"**

### Zarządzanie scenariuszami

- ✏️ **Edycja** - modyfikacja parametrów (tylko dla nieużywanych)
- 📋 **Duplikacja** - skopiuj scenariusz jako szablon
- 🗑️ **Usuwanie** - pojedyncze lub zbiorcze (checkbox + "Usuń zaznaczone")
- 📁 **Archiwizacja** - przeniesienie do archiwum bez usuwania

---

## Uruchamianie Optymalizacji

### Rozpoczęcie zadania

1. Przejdź do **"Optymalizacja" → zakładka "Scenariusze"**
2. Znajdź scenariusz na liście
3. Kliknij przycisk **"Uruchom"** ▶️
4. (Opcjonalnie) Dostosuj parametry wykonania:
   - Nazwa zadania
   - Max iteracji (override scenariusza)
   - Priorytet (high/normal/low)

5. Kliknij **"Start Optimization"**

### Co się dzieje w tle?

```
┌─────────────────┐
│ Utworzenie      │
│ zadania w DB    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Celery Worker   │
│ odbiera zadanie │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Inicjalizacja   │
│ modelu fizyki   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SLSQP optimizer │
│ (scipy.optimize)│
└────────┬────────┘
         │
         ▼ (iteracje)
┌─────────────────┐
│ Obliczenia      │
│ termodynamiczne │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Zapis wyników   │
│ do bazy danych  │
└─────────────────┘
```

### Szacowany czas wykonania

- **10 iteracji**: ~5-10 sekund
- **100 iteracji**: ~30-60 sekund (zalecane)
- **1000 iteracji**: ~5-10 minut (dla wysokiej precyzji)

⏱️ **Tip**: Zacznij od 50-100 iteracji, następnie zwiększ jeśli potrzeba większej dokładności.

---

## Monitorowanie Postępów

### Widok zadań

Przejdź do **"Optymalizacja" → zakładka "Zadania"**

### Status zadania

| Status | Ikona | Znaczenie |
|--------|-------|-----------|
| **Pending** | ⏳ | Oczekuje na wolny worker |
| **Initializing** | 🔄 | Przygotowanie modelu fizyki |
| **Running** | ▶️ | Optymalizacja w toku |
| **Completed** | ✅ | Zakończone sukcesem |
| **Failed** | ❌ | Błąd podczas wykonania |
| **Cancelled** | ⛔ | Anulowane przez użytkownika |

### Pasek postępu

Dla zadań **Running** wyświetlany jest:
- **Procent ukończenia** (0-100%)
- **Aktualna iteracja** / Max iteracji
- **Czas wykonania** (elapsed time)
- **Szacowany czas do końca** (ETA)

### Auto-odświeżanie

- **Przycisk ▶ Auto**: Włącz/wyłącz auto-odświeżanie co 5s
- **Przycisk 🔄 Odśwież**: Ręczne odświeżenie listy zadań
- Auto-odświeżanie aktywuje się automatycznie gdy są zadania running/pending

### Akcje na zadaniach

- **⏸️ Anuluj** - zatrzymanie zadania w trakcie (tylko dla running)
- **📊 Zobacz wyniki** - przejście do wyników (tylko dla completed)
- **🗑️ Usuń** - usunięcie zadania (tylko dla completed/failed/cancelled)
- **☑️ Zaznacz + Usuń zaznaczone** - usuwanie zbiorcze

---

## Przeglądanie Wyników

### Otwieranie wyników

1. Przejdź do **"Optymalizacja" → zakładka "Wyniki"**
2. Kliknij **"Zobacz wyniki"** przy wybranym zadaniu

### Sekcje wyników

#### 1. Metryki kluczowe (4 karty)

**Efektywność termiczna**
- Wartość: 98.64% (przykład)
- Zmiana: +7.15% vs baseline
- Interpretacja: Procent ciepła odzyskanego ze spalin

**Opór przepływu**
- Wartość: 67.01 Pa
- Zmiana: -739% (wzrost oporów - normalne dla zwiększonej powierzchni)
- Interpretacja: Spadek ciśnienia w regeneratorze

**Współczynnik wymiany ciepła (HTC)**
- Wartość: 27.84 W/(m²·K)
- Interpretacja: Intensywność wymiany ciepła

**Liczba jednostek transportu (NTU)**
- Wartość: 194.34
- Interpretacja: Efektywność wymiennika (wyższa = lepiej)

#### 2. Analiza ekonomiczna

- **Oszczędności paliwa**: 7.15% rocznie
- **Redukcja CO₂**: 6.79% rocznie (kg/rok)
- **Oszczędności finansowe**: $357,320 / rok
- **Okres zwrotu**: 24 miesiące

💡 **Wskazówka**: Okres zwrotu < 36 miesięcy jest uznawany za bardzo opłacalny.

#### 3. Zmienne projektowe - wartości optymalne

| Zmienna | Wartość początkowa | Wartość optymalna | Zmiana |
|---------|-------------------|-------------------|---------|
| Wysokość checkera | 0.5 m | 2.0 m | +300% |
| Grubość ścianki | 0.5 m | 0.8 m | +60% |
| Rozstaw checkerów | 0.1 m | 0.05 m | -50% |

#### 4. Wykres zbieżności

Wykres pokazuje:
- **Niebieska linia**: Aktualna wartość funkcji celu
- **Pomarańczowa linia**: Najlepsza znaleziona wartość
- **Oś X**: Numer iteracji
- **Oś Y**: Wartość funkcji celu (ujemna dla maksymalizacji)

**Interpretacja**:
- Spadek krzywej = poprawa wyniku
- Plateau = osiągnięcie optimum
- Oscylacje = eksploracja przestrzeni rozwiązań

#### 5. Dodatkowe metryki

Porównanie baseline vs. optymalizowane:
- Przepływ masy spalin
- Temperatura wlotu/wylotu
- Powierzchnia wymiany ciepła
- Straty ciepła przez ścianki
- Liczby Reynolds i Nusselt

#### 6. Metryki jakości rozwiązania

- **Feasibility (wykonalność)**: 0.5 = częściowo wykonalne
- **Confidence (pewność)**: 0.3 = niska pewność (wymaga weryfikacji)
- **Convergence achieved**: Czy algorytm osiągnął zbieżność

⚠️ **Uwaga**: Niska confidence sugeruje, że warto:
- Zwiększyć liczbę iteracji
- Sprawdzić ograniczenia (constraints)
- Zweryfikować dane wejściowe

### Eksport wyników

- **📄 PDF**: Raport techniczny (grafika + tabele)
- **📊 Excel**: Dane do dalszej analizy
- **📋 JSON**: Format surowych danych dla developerów

---

## Baza Materiałów

### Przeglądanie materiałów

Przejdź do **"Materiały"** w menu głównym

System zawiera **111 materiałów** podzielonych na kategorie:

#### Kategorie materiałów

1. **Cegły szamotowe** (Fireclay Bricks)
   - Standard duty, High duty, Super duty
   - Temperatura maks: 1400-1600°C

2. **Cegły krzemionkowe** (Silica Bricks)
   - Wysoka odporność termiczna (1650°C)
   - Niski współczynnik rozszerzalności

3. **Cegły magnezytowe** (Magnesia Bricks)
   - Temperatura maks: 1800°C
   - Odporność na zasady

4. **Cegły chromowo-magnezytowe**
   - Ultra wysokie temperatury (2000°C)
   - Dla pieców specjalnych

5. **Materiały izolacyjne**
   - Wełna ceramiczna, włókna szklane
   - Cegły izolacyjne lekkie

6. **Betonony ogniotrwałe**
   - Castable refractories
   - Łatwe w aplikacji

### Parametry materiałów

Dla każdego materiału dostępne są:
- **Przewodność cieplna** λ [W/(m·K)]
- **Ciepło właściwe** Cp [J/(kg·K)]
- **Gęstość** ρ [kg/m³]
- **Maksymalna temperatura** Tmax [°C]
- **Odporność chemiczna** (kwasy/zasady)
- **Koszt** [$/kg] - orientacyjny

### Filtrowanie i wyszukiwanie

- 🔍 **Szukaj po nazwie** - pole tekstowe
- 🏷️ **Filtruj po kategorii** - dropdown
- 🌡️ **Filtruj po temperaturze** - min/max slider
- 💰 **Filtruj po koszcie** - zakres cenowy

### Dodawanie własnych materiałów

(Funkcja dla ADMIN)

1. Kliknij **"Dodaj materiał"**
2. Wypełnij formularz z właściwościami
3. Dodaj krzywe temperatura-właściwość (opcjonalnie)
4. Zapisz

---

## Raporty

### Generowanie raportów

1. Przejdź do **"Raporty"** w menu głównym
2. Wybierz typ raportu:

#### Typy raportów

**Raport optymalizacji**
- Szczegóły pojedynczego zadania
- Format: PDF, Excel
- Zawiera: wykresy, tabele, rekomendacje

**Raport porównawczy**
- Porównanie wielu konfiguracji
- Analiza sensitivity
- Ranking rozwiązań

**Raport miesięczny**
- Podsumowanie wszystkich optymalizacji
- Statystyki systemowe
- Trendy efektywności

**Raport finansowy**
- Łączne oszczędności
- ROI (return on investment)
- Projekcje przyszłe

3. Wybierz zakres dat / zadania do uwzględnienia
4. Kliknij **"Generuj raport"**
5. Pobierz plik po wygenerowaniu

### Harmonogramy raportów

(Funkcja dla ADMIN)

Automatyczne generowanie raportów:
- **Codziennie** o 06:00 - raport dzienny
- **Co tydzień** w poniedziałek - raport tygodniowy
- **Co miesiąc** 1. dnia miesiąca - raport miesięczny

Email z raportem wysyłany na skonfigurowane adresy.

---

## Rozwiązywanie Problemów

### Najczęstsze problemy

#### ❌ "Nie mogę się zalogować"

**Możliwe przyczyny:**
1. Nieprawidłowe hasło
   - ✅ **Rozwiązanie**: Użyj domyślnego `admin` / `admin`
   - ✅ Skontaktuj się z administratorem o reset hasła

2. Serwer nie odpowiada
   - ✅ Sprawdź czy backend działa: http://localhost:8000/health
   - ✅ Powinien zwrócić: `{"status":"healthy","service":"fro-api"}`

3. Problem z sesją
   - ✅ Wyczyść cookies przeglądarki (Ctrl+Shift+Delete)
   - ✅ Odśwież stronę (Ctrl+F5)

#### ⏳ "Zadanie utknęło w statusie Pending"

**Możliwe przyczyny:**
1. Brak wolnych Celery workers
   - ✅ Zaczekaj 1-2 minuty
   - ✅ Anuluj zadanie i uruchom ponownie

2. Problem z kolejką Redis
   - ✅ Skontaktuj się z administratorem

#### ❌ "Optymalizacja kończy się błędem Failed"

**Sprawdź komunikat błędu** (kliknij zadanie → szczegóły):

**"ValueError: Job not found"**
- Zadanie zostało usunięte podczas wykonywania
- ✅ Utwórz nowe zadanie

**"RuntimeError: Event loop"**
- Problem techniczny z workerem
- ✅ Zrestartuj zadanie
- ✅ Jeśli powtarza się - zgłoś administratorowi

**"Invalid configuration"**
- Błędne dane wejściowe
- ✅ Sprawdź konfigurację bazową (temperatura, przepływy)
- ✅ Upewnij się że zakresy zmiennych są realistyczne

#### 📊 "Wyniki wyglądają nierealistycznie"

**Zbyt dobra efektywność (>99%)**
- Sprawdź dane wejściowe (szczególnie temperatury)
- Porównaj z wartościami referencyjnymi
- Zwiększ liczbę iteracji dla lepszej precyzji

**Ujemne oszczędności**
- Może oznaczać że konfiguracja bazowa była już bliska optimum
- Sprawdź czy zmienne projektowe mają odpowiednie zakresy

**Bardzo długi okres zwrotu (>60 miesięcy)**
- Sprawdź koszty materiałów
- Oceń czy zmiana geometrii jest zbyt drastyczna

#### 🔄 "Auto-odświeżanie nie działa"

1. Sprawdź czy przycisk "Auto" jest zielony (włączony)
2. Upewnij się że przeglądarka nie blokuje JavaScript
3. Odśwież stronę ręcznie przyciskiem 🔄

#### 🗑️ "Nie mogę usunąć scenariusza/zadania"

**Scenariusz**:
- Nie można usunąć scenariusza który ma aktywne zadania (running)
- ✅ Anuluj zadania, potem usuń scenariusz

**Zadanie**:
- Zadanie running/pending nie może być usunięte
- ✅ Użyj przycisku "Anuluj" najpierw
- ✅ Po anulowaniu możesz usunąć

### Kontakt z supportem

Jeśli problem się powtarza lub jest krytyczny:

📧 **Email**: support@forglass.com
📞 **Telefon**: +48 XX XXX XXXX (8:00-16:00, PN-PT)
🐛 **Zgłoszenia błędów**: https://github.com/forglass/fro/issues

Przy zgłaszaniu problemu podaj:
- Wersję systemu (widoczną w stopce)
- Opis problemu krok po kroku
- Screenshot błędu (jeśli dotyczy)
- ID zadania/scenariusza (jeśli dotyczy)

---

## Słownik terminów

- **Checker** - warstwowy element ogniotrwały w regeneratorze, przez który przepływają spaliny
- **NTU** - Number of Transfer Units, bezwymiarowa liczba określająca efektywność wymiennika
- **SLSQP** - Sequential Least Squares Programming, algorytm optymalizacji gradientowej
- **Baseline** - konfiguracja wyjściowa, punkt odniesienia do porównania
- **Objective function** - funkcja celu, wartość którą optymalizujemy (minimalizujemy lub maksymalizujemy)
- **Convergence** - zbieżność, stan gdy algorytm osiągnął optimum i przestał się poprawiać
- **Feasibility** - wykonalność, stopień spełnienia ograniczeń fizycznych
- **HTC** - Heat Transfer Coefficient, współczynnik wymiany ciepła [W/(m²·K)]
- **Reynolds number** - liczba Reynoldsa, bezwymiarowy parametr charakteryzujący przepływ
- **Nusselt number** - liczba Nusselta, bezwymiarowy współczynnik wymiany ciepła

---

## Dodatek A: Klawiszologia

| Skrót | Akcja |
|-------|-------|
| `Ctrl + K` | Otwórz wyszukiwarkę globalną |
| `Ctrl + /` | Pokaż pomoc kontekstową |
| `Esc` | Zamknij modal/dialog |
| `Tab` | Nawigacja między polami formularza |
| `Enter` | Zatwierdź formularz |
| `Ctrl + S` | Zapisz (w formularzach) |

---

## Dodatek B: Najlepsze praktyki

### Przed uruchomieniem optymalizacji

1. ✅ Zweryfikuj dane wejściowe (temperatury, przepływy)
2. ✅ Sprawdź czy materiały są dostępne w bazie
3. ✅ Ustaw realistyczne zakresy zmiennych projektowych
4. ✅ Zacznij od małej liczby iteracji (50-100) jako test
5. ✅ Sprawdź czy konfiguracja bazowa jest poprawnie zdefiniowana

### Podczas optymalizacji

1. ⏱️ Pozwól algorytmowi pracować - nie przerywaj przedwcześnie
2. 📊 Monitoruj wykres zbieżności - plateau = dobry znak
3. ⚡ Dla szybkich testów: 10-50 iteracji
4. 🎯 Dla produkcji: 100-500 iteracji
5. 🔬 Dla badań naukowych: 500-1000 iteracji

### Po otrzymaniu wyników

1. 🔍 Sprawdź feasibility i confidence
2. 📊 Porównaj z wartościami referencyjnymi z literatury
3. 💰 Oceń okres zwrotu inwestycji
4. 🔄 Uruchom ponownie z większą liczbą iteracji jeśli confidence < 0.5
5. 📝 Wygeneruj raport dla dokumentacji

---

## Historia wersji

- **v1.0** (2025-10-02) - Wersja produkcyjna MVP
  - Optymalizacja SLSQP
  - Baza 111 materiałów
  - System raportowania PDF/Excel
  - Dashboard z metrykami

---

**© 2025 Forglass Sp. z o.o. Wszystkie prawa zastrzeżone.**

*Dokument wygenerowany automatycznie przez Forglass Regenerator Optimizer v1.0*
