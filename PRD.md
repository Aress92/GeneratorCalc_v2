Spis treści
Metadane dokumentu

Streszczenie wykonawcze

Wizja i cele biznesowe

Analiza użytkowników

Zakres MVP

Przepływy użytkownika

Wymagania funkcjonalne

Wymagania niefunkcjonalne

Raporty i eksporty

Integracje i formaty danych

Ograniczenia i założenia

Kluczowe wskaźniki wydajności

Ryzyka i mitigacje

Definition of Done

Plan UAT

Słownik pojęć

Changelog

Metadane dokumentu
Pole	Wartość
Tytuł	Product Requirements Document - Forglass Regenerator Optimizer
Wersja	1.0.0
Data	2025-09-23
Status	Draft - Ready for Review
Właściciel	Product Owner / Senior Full-Stack Architect
Stakeholders	Forglass Engineering Team, Plant Operations, IT Department
Zatwierdzenie	Pending CTO approval
Streszczenie wykonawcze
Forglass Regenerator Optimizer (FRO) to specjalistyczny system wspomagający inżynierów w optymalizacji regeneratorów pieców szklarskich. System pozwala na import danych technicznych, konfigurację parametrów regeneratorów, uruchomienie zaawansowanych obliczeń optymalizacyjnych oraz generowanie szczegółowych raportów. Głównym celem jest redukcja zużycia paliwa o 5-15% i obniżenie emisji CO₂ przy zachowaniu stabilności procesów termicznych.

System będzie działał w pełni on-premise w infrastrukturze klienta, zapewniając pełną kontrolę nad danymi przemysłowymi i spełnienie wymagań bezpieczeństwa.

Wizja i cele biznesowe
Wizja produktu
"Być wiodącym narzędziem optymalizacji energetycznej w przemyśle szklarskim, umożliwiającym inżynierom podejmowanie decyzji opartych na danych i osiąganie wymiernych korzyści środowiskowych i ekonomicznych."

Cele biznesowe
Cel	Metryka sukcesu	Termin
Redukcja zużycia energii	5-15% oszczędności paliwa w pilotażowych instalacjach	Q2 2026
Zwiększenie wydajności inżynierów	50% skrócenie czasu analiz termodynamicznych	Q1 2026
Standaryzacja procesów	100% scenariuszy z audytowalną dokumentacją	Q1 2026
Adopcja produktu	80% zespołu inżynierskiego używa systemu regularnie	Q3 2026
ROI	Zwrot z inwestycji < 18 miesięcy	Q4 2026
Problem biznesowy
Wysokie koszty energii: Regeneratory stanowią 60-70% zużycia energii w piecu

Brak narzędzi optymalizacji: Inżynierowie bazują na doświadczeniu i prostych kalkulatorach

Długi czas analiz: Manualne obliczenia zajmują 2-4 dni na scenariusz

Brak powtarzalności: Różne podejścia różnych inżynierów do tych samych problemów

Ograniczona audytowalność: Trudność w udokumentowaniu przesłanek decyzji

Analiza użytkowników
Persona 1: Inżynier Procesu (Primary User)
Profile:

Role: Senior Process Engineer

Experience: 5-15 lat w przemyśle szklarskim

Technical Skills: Excel expert, podstawy programowania

Pain Points: Czasochłonne obliczenia, brak narzędzi do optymalizacji

Goals: Szybka analiza scenariuszy, wiarygodne wyniki, dokumentacja decyzji

User Stories:

text
# US-001: Import danych technicznych
Given jestem inżynierem procesu z danymi regeneratora w Excel
When importuję plik XLSX z konfiguracją regeneratora
Then system waliduje dane i tworzy model 3D regeneratora
And widzę podgląd geometrii oraz potwierdzenie poprawności danych
And mogę skorygować błędy przed zapisem do systemu

# US-002: Konfiguracja scenariusza optymalizacji  
Given mam zaimportowany model regeneratora
When tworzę nowy scenariusz optymalizacji
Then system prowadzi mnie przez wizard konfiguracji
And mogę ustawić zmienne optymalizacyjne, ograniczenia i cele
And widzę estymację czasu obliczeń przed uruchomieniem

# US-003: Monitorowanie optymalizacji w czasie rzeczywistym
Given uruchomiłem optymalizację scenariusza
When obserwuję postęp obliczeń
Then widzę aktualną iterację, wartość funkcji celu i zbieżność
And mogę wstrzymać lub przerwać optymalizację w dowolnym momencie
And otrzymuję powiadomienie o zakończeniu obliczeń
Persona 2: UTR/Automatyk (Secondary User)
Profile:

Role: Automation Engineer / Control Systems Specialist

Experience: 3-10 lat w automatyce przemysłowej

Technical Skills: SCADA, PLC, podstawy termodynamiki

Pain Points: Brak integracji z systemami sterowania

Goals: Monitoring parametrów, alerty, integracja z DCS

User Stories:

text
# US-004: Monitoring wskaźników wydajności
Given jestem odpowiedzialny za monitoring regeneratorów
When przeglądam dashboard wydajności 
Then widzę kluczowe wskaźniki (temperatura, delta-P, efficiency)
And otrzymuję alerty przy przekroczeniu thresholds
And mogę eksportować dane do systemów SCADA

# US-005: Analiza trendów historycznych
Given potrzebuję przeanalizować wydajność w czasie
When wybieram zakres dat i regenerator
Then widzę wykresy trendów kluczowych parametrów
And mogę porównać różne okresy działania
And identyfikuję anomalie i patterny degradacji
Persona 3: Kierownik Produkcji (Business User)
Profile:

Role: Production Manager

Experience: 10-20 lat w zarządzaniu produkcją

Technical Skills: Business focus, podstawy techniczne

Pain Points: Brak KPI energetycznych, długi czas decyzji

Goals: Raporty biznesowe, ROI, compliance

User Stories:

text
# US-006: Raporty wykonawcze i KPI
Given potrzebuję regularnych raportów o wydajności energetycznej
When generuję miesięczny raport wykonawczy
Then otrzymuję PDF z KPI, trendami i rekomendacjami
And raport zawiera porównanie z celami biznesowymi
And mogę udostępnić raport zarządowi i klientom

# US-007: Analiza ROI projektów optymalizacyjnych
Given rozważam inwestycję w modernizację regeneratora
When porównuję scenariusze before/after
Then widzę prognozowane oszczędności i okres zwrotu
And otrzymuję business case z uzasadnieniem inwestycji
And mam dokumentację do procesu zatwierdzenia budżetu
Persona 4: Administrator Systemu (Technical User)
Profile:

Role: IT Administrator / DevOps Engineer

Experience: 5-15 lat w IT/OT systems

Technical Skills: Servers, networks, databases, security

Pain Points: Kompleksowe wdrożenia, bezpieczeństwo, backup

Goals: Stabilne działanie, security, monitoring, disaster recovery

User Stories:

text
# US-008: Zarządzanie użytkownikami i uprawnieniami
Given jestem administratorem systemu
When zarządzam kontami użytkowników
Then mogę tworzyć konta, przypisywać role (ADMIN/ENGINEER/VIEWER)
And widzę logi aktywności wszystkich użytkowników  
And mogę blokować konta i resetować hasła
And system loguje wszystkie akcje administracyjne

# US-009: Monitoring systemu i alerting
Given odpowiadam za dostępność systemu
When monitoruję infrastrukturę
Then widzę dashboardy z metrykami (CPU, memory, storage, response times)
And otrzymuję alerty email/SMS przy problemach
And mam dostęp do logów aplikacji i audytu
Zakres MVP
Moduł 1: Import i walidacja danych (Must Have)
Funkcjonalności:

Import plików XLSX z templates dla różnych typów regeneratorów

Dry-run preview z walidacją danych przed zapisem

Mapowanie kolumn (drag & drop interface)

Konwersje jednostek (metryczne/imperialne)

Walidacja fizyczna (sprawdzenie spójności geometric i thermal properties)

Bulk import z progress tracking

Kryteria akceptacji:

Import pliku 1MB (1000 rekordów) < 15 sekund

Skuteczność walidacji błędów ≥ 95%

Obsługa 5 formatów templates (checker patterns, wall configurations)

Podgląd 3D geometry po imporcie

Moduł 2: Konfigurator regeneratora (Must Have)
Funkcjonalności:

Step-by-step wizard konfiguracji

Wizualizacja 3D regeneratora

Biblioteka materiałów z właściwościami termicznymi

Walidacja constraintów fizycznych (geometry, flow rates, temperatures)

Templates dla typowych konfiguracji (crown, end-port, cross-fired)

Save/load konfiguracji jako JSON

Kryteria akceptacji:

Wizard maksymalnie 7 kroków

3D preview z WebGL/Three.js

Biblioteka ≥ 50 materiałów z wersjami

Walidacja real-time z feedback

Moduł 3: Silnik optymalizacji (Must Have)
Funkcjonalności:

Konfiguracja celów optymalizacji (minimize fuel consumption, maximize efficiency)

Wybór algorytmu (SLSQP default, COBYLA fallback)

Server-Sent Events z progress tracking

Pause/Resume/Cancel functionality

Parallel scenarios (queue management)

Convergence criteria customization

Kryteria akceptacji:

Optymalizacja referencyjna ≤ 2 minuty

Real-time progress updates co 2 sekundy

Graceful handling pause/resume

Kolejkowanie do 10 zadań równoczesnych

Moduł 4: Wyniki i raporty (Must Have)
Funkcjonalności:

Porównanie scenariuszy (side-by-side comparison)

Interactive charts z Plotly.js

Export do PDF (executive summary + technical details)

Export do XLSX (raw data + charts)

Digital signature raportu (SHA-256 hash + metadata)

Email sharing z secure links

Kryteria akceptacji:

Generowanie raportu PDF < 30 sekund

Porównanie do 5 scenariuszy równocześnie

PDF zawiera branding klienta

XLSX z co najmniej 5 arkuszami danych

Moduł 5: RBAC i audit (Must Have)
Funkcjonalności:

Role-based access control (Admin/Engineer/Viewer)

JWT authentication z HttpOnly cookies

Audit log wszystkich działań użytkowników

Session management z timeout

Password policy enforcement

User activity dashboard dla adminów

Kryteria akceptacji:

Login/logout < 2 sekundy

Session timeout po 8h nieaktywności

Audit log retention 2 lata

RBAC coverage 100% endpointów

Moduł 6: Katalog materiałów (Must Have)
Funkcjonalności:

CRUD operations na materiałach

Versioning materiałów z changelog

Import materiałów z external sources

Search/filter z faceted navigation

Material properties validation

Approval workflow dla nowych materiałów

Kryteria akceptacji:

Baza startowa ≥ 100 materiałów

Search results < 200ms

Version control z diff view

Approval w ≤ 2 krokach

Przepływy użytkownika
User Flow 1: Import i walidacja danych XLSX
text
flowchart TD
    A[Wybierz plik XLSX] --> B{Wykryj format}
    B -->|Format rozpoznany| C[Mapowanie kolumn]
    B -->|Format nieznany| D[Ręczne mapowanie]
    
    C --> E[Preview danych]
    D --> E
    
    E --> F{Walidacja}
    F -->|Błędy krytyczne| G[Pokaż błędy]
    F -->|Ostrzeżenia| H[Pokaż ostrzeżenia]
    F -->|OK| I[Konwersja jednostek]
    
    G --> J[Popraw dane]
    H --> K{Kontynuować?}
    K -->|Tak| I
    K -->|Nie| J
    J --> E
    
    I --> L[Dry-run simulation]
    L --> M{Wyniki OK?}
    M -->|Nie| N[Raport błędów]
    M -->|Tak| O[Zapisz do bazy]
    
    N --> J
    O --> P[Sukces - pokaż summary]
User Flow 2: Konfiguracja scenariusza optymalizacji
text
flowchart TD
    A[Start: Nowy scenariusz] --> B[Wybierz regenerator]
    B --> C[Wizard: Krok 1 - Cele optymalizacji]
    
    C --> D[Krok 2 - Zmienne optymalizacyjne]
    D --> E[Krok 3 - Constrainty]
    E --> F[Krok 4 - Parametry algorytmu]
    F --> G[Krok 5 - Review konfiguracji]
    
    G --> H{Walidacja}
    H -->|Błędy| I[Pokaż błędy walidacji]
    H -->|Ostrzeżenia| J[Pokaż ostrzeżenia + opcja kontynuuj]
    H -->|OK| K[Estymacja czasu]
    
    I --> L[Wróć do edycji]
    J --> M{Kontynuować mimo ostrzeżeń?}
    M -->|Nie| L
    M -->|Tak| K
    L --> D
    
    K --> N[Zapisz scenariusz]
    N --> O{Uruchom teraz?}
    O -->|Tak| P[Dodaj do kolejki]
    O -->|Nie| Q[Zapisz jako draft]
    
    P --> R[Start optymalizacji]
    Q --> S[Powrót do listy]
User Flow 3: Monitoring i zarządzanie optymalizacją
text
flowchart TD
    A[Uruchomienie optymalizacji] --> B[SSE Connection]
    B --> C[Real-time progress]
    
    C --> D{Status update}
    D -->|Progress| E[Update UI: iteracja, objective value]
    D -->|Completed| F[Show results]
    D -->|Error| G[Show error message]
    D -->|Paused| H[Show pause state]
    
    E --> I{User action}
    I -->|Monitor| C
    I -->|Pause| J[Send pause signal]
    I -->|Cancel| K[Send cancel signal]
    
    J --> L[Confirm pause]
    L --> H
    
    H --> M{Resume action}
    M -->|Resume| N[Send resume signal]
    M -->|Cancel| K
    N --> C
    
    K --> O[Confirm cancellation]
    O --> P[Job cancelled]
    
    F --> Q[Generate report]
    G --> R[Error handling/retry]
    P --> S[Return to dashboard]
    Q --> S
    R --> S
Wymagania funkcjonalne
ID	Opis wymagania	Priorytet	Kryteria akceptacji	Metryki
FR-001	System umożliwia import danych z plików XLSX	Must Have	Upload pliku ≤10MB, walidacja w <30s, preview danych	Success rate ≥95%
FR-002	Mapowanie kolumn między plikiem a schematem danych	Must Have	Drag&drop interface, auto-detection, custom mapping	Time to map <2 min
FR-003	Konwersje jednostek (metric ↔ imperial)	Must Have	Support dla 20+ jednostek, accuracy 99.9%	Zero errors in conversion
FR-004	Walidacja fizyczna danych regeneratora	Must Have	Geometry validation, thermal properties check	≥95% błędów wykrytych
FR-005	Wizard konfiguracji scenariusza optymalizacji	Must Have	Max 7 kroków, progress indicator, back/forward	Completion rate ≥80%
FR-006	Wizualizacja 3D regeneratora	Should Have	WebGL rendering, zoom/rotate/pan, section views	Load time <5s
FR-007	Biblioteka materiałów z wersjami	Must Have	CRUD operations, search, versioning, approval	≥100 materiałów w start
FR-008	Silnik optymalizacji SLSQP	Must Have	Minimize fuel consumption, constraint handling	Reference case <2 min
FR-009	Real-time progress tracking optymalizacji	Must Have	SSE stream, iteration count, objective value	Update co 2s
FR-010	Pause/Resume/Cancel optymalizacji	Should Have	Graceful handling, state preservation	Recovery success ≥95%
FR-011	Porównanie wyników scenariuszy	Must Have	Side-by-side comparison, diff highlighting	Max 5 scenariuszy
FR-012	Eksport raportów do PDF	Must Have	Executive + technical sections, branding	Generation <30s
FR-013	Eksport danych do XLSX	Must Have	Raw data + charts, multiple sheets	All data included
FR-014	RBAC z rolami Admin/Engineer/Viewer	Must Have	Role-based permissions, secure endpoints	100% endpoint coverage
FR-015	JWT authentication z HttpOnly cookies	Must Have	Secure login/logout, session management	Brute-force protection
FR-016	Audit log działań użytkowników	Must Have	All CRUD operations logged, retention 2y	100% action coverage
FR-017	Dashboard z kluczowymi metrykami	Should Have	KPI widgets, trends, alerts	Load time <3s
FR-018	Search i filtering w katalogach	Must Have	Full-text search, faceted filtering	Results <200ms
FR-019	Bulk operations (import/export/delete)	Should Have	Progress tracking, error handling	Success rate ≥90%
FR-020	Email notifications dla zdarzeń	Could Have	Job completion, errors, alerts	Delivery <1 min
Wymagania niefunkcjonalne
Kategoria	Wymaganie	Metryka docelowa	Priorytet	Test method
Performance	Czas odpowiedzi API	P95 < 200ms	Must Have	Load testing
Performance	Throughput API	100 req/s @ 80% CPU	Must Have	Stress testing
Performance	Czas optymalizacji	Reference case < 2 min	Must Have	Benchmark suite
Performance	Import XLSX	10MB file < 30s	Must Have	Performance testing
Performance	3D rendering	Model load < 5s	Should Have	Browser testing
Scalability	Concurrent users	50 active users	Must Have	Load testing
Scalability	Concurrent optimizations	10 parallel jobs	Must Have	Queue testing
Scalability	Database growth	100GB+ data support	Should Have	Volume testing
Availability	System uptime	99.5% (≤4h/month planned)	Must Have	Monitoring
Availability	Recovery time	RTO < 4h, RPO < 1h	Must Have	DR testing
Reliability	Job completion rate	≥95% success rate	Must Have	Statistics
Reliability	Data integrity	Zero data loss	Must Have	Backup testing
Security	Authentication	JWT + RBAC	Must Have	Security audit
Security	Data encryption	TLS 1.3 + AES-256	Must Have	Penetration test
Security	Session timeout	8h inactivity	Must Have	Security testing
Security	Password policy	8+ chars, complexity	Must Have	Policy testing
Usability	Learning curve	<4h training for engineer	Should Have	User testing
Usability	Task completion time	50% reduction vs manual	Should Have	Time studies
Usability	Mobile responsiveness	Tablet support (viewing)	Could Have	Responsive testing
Maintainability	Code coverage	Backend ≥80%, Frontend ≥70%	Must Have	Automated testing
Maintainability	Documentation	API 100%, architecture current	Must Have	Review process
Portability	Browser support	Chrome, Firefox, Edge latest	Must Have	Cross-browser testing
Portability	Operating system	Linux containers only	Must Have	Deployment testing
Raporty i eksporty
Executive Summary Report (PDF)
Zawartość raportu:

Cover page: Logo klienta, tytuł projektu, data, autor

Executive Summary: Kluczowe wyniki, rekomendacje, ROI

Scenario Comparison: Tabela porównawcza głównych wskaźników

Key Performance Indicators: Fuel consumption, efficiency, emissions

Recommendations: Top 3 działania z największym impact

Financial Impact: Projected savings, payback period

Technical Appendix: Detailed calculations, assumptions

Signature Page: Digital signature (SHA-256 hash + metadata)

Metadane raportu:

json
{
  "report_id": "RPT-20250923-001",
  "generated_by": "Jan Kowalski",
  "generated_at": "2025-09-23T17:48:00Z",
  "scenario_ids": ["uuid1", "uuid2"],
  "hash_sha256": "a1b2c3d4...",
  "version": "1.0",
  "classification": "Internal Use"
}
Technical Data Export (XLSX)
Arkusze danych:

Summary: Zestawienie wyników wszystkich scenariuszy

Input_Data: Dane wejściowe (geometry, materials, operating conditions)

Optimization_Results: Szczegółowe wyniki optymalizacji

Iteration_History: History wszystkich iteracji algorytmu

Charts: Embedded charts (convergence, sensitivity analysis)

Material_Properties: Właściwości wszystkich użytych materiałów

Calculations: Detailed calculations and formulas used

Metadata: Report info, timestamp, user, system version

Format danych:

Precyzja: 6 miejsc po przecinku dla wartości fizycznych

Jednostki: Clearly labeled in column headers

Walidacja: Excel data validation rules included

Charts: Native Excel charts with data series

Automated Report Delivery
Email template:

xml
<h2>Forglass Regenerator Optimizer - Report Generated</h2>
<p>Dear {{user_name}},</p>
<p>Your optimization report for scenario "{{scenario_name}}" has been generated.</p>

<h3>Key Results:</h3>
<ul>
  <li>Fuel savings: {{fuel_savings}}% ({{cost_savings}} USD/year)</li>
  <li>CO2 reduction: {{co2_reduction}} tonnes/year</li>
  <li>Payback period: {{payback_months}} months</li>
</ul>

<p>Download links (valid for 7 days):</p>
<ul>
  <li><a href="{{pdf_link}}">Executive Report (PDF)</a></li>
  <li><a href="{{xlsx_link}}">Technical Data (XLSX)</a></li>
</ul>

<p>Report ID: {{report_id}}<br/>
Generated: {{timestamp}}</p>
Integracje i formaty danych
Supported Import Formats
Format	Opis	Use Case	Validation
XLSX Template v1	Checker pattern configuration	Material properties, geometry	Schema validation
XLSX Template v2	Wall configuration	Insulation, refractory data	Physics validation
XLSX Template v3	Operating conditions	Temperatures, flow rates	Range validation
CSV Delimited	Bulk material import	Material database updates	Format validation
JSON Config	Scenario parameters	API integration, backup/restore	JSON schema
Data Conversion Rules
Units conversion:

python
# Temperature conversions
celsius_to_fahrenheit = lambda c: c * 9/5 + 32
fahrenheit_to_celsius = lambda f: (f - 32) * 5/9
celsius_to_kelvin = lambda c: c + 273.15

# Thermal properties
btu_to_watt = lambda btu: btu * 0.29307107
w_mk_to_btu_ft_hr_f = lambda w: w * 0.5777

# Flow rates  
scfm_to_m3h = lambda scfm: scfm * 1.69901
Material properties dictionary:

Thermal conductivity: W/(m·K), BTU/(ft·hr·°F)

Specific heat: kJ/(kg·K), BTU/(lb·°F)

Density: kg/m³, lb/ft³

Porosity: % (0-100)

Surface area: m²/m³, ft²/ft³

Export Formats
Format	Content	Audience	Delivery
PDF Report	Executive summary + technical details	Management, engineers	Email, web download
XLSX Data	Raw data + charts	Engineers, analysts	Web download, API
JSON API	Scenario results	External systems	REST API
CSV Export	Tabular data	Spreadsheet analysis	Web download
API Integration Points
Webhook notifications:

json
{
  "event": "optimization.completed",
  "timestamp": "2025-09-23T17:48:00Z",
  "data": {
    "scenario_id": "uuid",
    "user_id": "uuid", 
    "results": {
      "fuel_savings_percent": 12.5,
      "co2_reduction_tonnes": 145.2,
      "execution_time_seconds": 118
    }
  }
}
Ograniczenia i założenia
Ograniczenia techniczne
Ograniczenie	Impact	Mitigacja
On-premise only	Brak cloud scalability	Horizontal scaling na VM
Single-tenant	Shared nothing architecture	Resource isolation
MySQL only	Vendor lock-in risk	Migration scripts ready
SLSQP algorithm	Local optima risk	Multi-start optimization
CPU-bound calculations	Limited parallelization	Celery distributed workers
Memory constraints	Large models (>10GB) may fail	Chunked processing
Założenia biznesowe
Dane wejściowe: Użytkownicy dostarczą kompletne i poprawne dane techniczne

Expertise: Engineers mają podstawową wiedzę o termodynamice

Infrastructure: Klient zapewni infrastrukturę zgodną z wymaganiami

Support: 8x5 support window (business hours)

Training: 2 dni szkolenia na start + 4h remote per month

Updates: Quarterly releases z backward compatibility

Polityka retencji danych
Typ danych	Retencja	Archiwizacja	Usuwanie
Scenarios active	2 lata	Po 1 roku → cold storage	Soft delete
Audit logs	7 lat	Po 2 latach → archive	Hard delete
Job logs	90 dni	Brak	Hard delete
Reports	5 lat	Po 2 latach → NAS	Soft delete
User data	Do usunięcia konta	RODO compliance	Anonymizacja
Kluczowe wskaźniki wydajności
Business KPIs
KPI	Definicja	Target	Źródło danych	Frequency
Fuel Savings %	(Baseline - Optimized) / Baseline * 100	5-15%	Scenario results	Per optimization
CO2 Reduction	Tonnes CO2 reduced annually	100+ tonnes/year	Carbon calculations	Per scenario
ROI	(Savings - Investment) / Investment	<18 months payback	Financial model	Quarterly
User Adoption	Active users / Total licensed users	≥80%	Usage analytics	Monthly
Time to Insight	Days from data to recommendation	<1 day (was 2-4)	Process tracking	Per project
Decision Confidence	% scenarios with >90% confidence	≥85%	Model validation	Per optimization
Technical SLIs/SLOs
Metric	SLI Definition	SLO Target	Error Budget	Alert Threshold
Availability	Uptime / Total time	99.5%	0.5% (3.6h/month)	<99.0%
API Latency	P95 response time	<200ms	10% >200ms	P95 >300ms
Optimization Time	P90 completion time	<2 min	10% >2min	>5 min
Success Rate	Completed jobs / Total jobs	≥95%	5% failures	<90%
Data Quality	Valid imports / Total imports	≥95%	5% bad imports	<90%
Security	Failed auth / Total auth	<1%	Brute force limit	>5%
User Experience KPIs
KPI	Definition	Target	Measurement
Task Success Rate	Completed workflows / Started	≥90%	User analytics
Time on Task	Average time to complete scenario setup	<30 min	Time tracking
Error Recovery	Users who complete after error	≥80%	Error analytics
Feature Adoption	Users using advanced features	≥60%	Feature flags
Support Tickets	Support requests / Active users	<5% monthly	Ticket system
User Satisfaction	NPS score from quarterly survey	≥8/10	Survey results
System Health Metrics
python
# Prometheus metrics examples
optimization_duration_histogram = Histogram(
    'fro_optimization_duration_seconds',
    'Time spent on optimization jobs',
    ['algorithm', 'scenario_type'],
    buckets=[30, 60, 120, 300, 600, 1800, 3600]
)

api_requests_counter = Counter(
    'fro_api_requests_total', 
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

active_users_gauge = Gauge(
    'fro_active_users',
    'Number of active user sessions'
)

database_connections_gauge = Gauge(
    'fro_database_connections',
    'Active database connections'
)
Ryzyka i mitigacje
Ryzyka techniczne
Ryzyko	Prawdopodobieństwo	Impact	Mitigacja	Owner
Zbieżność algorytmu SLSQP	Średnie	Wysokie	Multi-start, fallback do COBYLA	Tech Lead
Performance przy dużych modelach	Średnie	Średnie	Chunked processing, memory optimization	Backend Dev
Błędy w danych importowanych	Wysokie	Średnie	Aggressive validation, user feedback	Product Owner
Browser compatibility	Niskie	Średnie	Cross-browser testing, progressive enhancement	Frontend Dev
Database corruption	Niskie	Wysokie	Daily backups, ACID transactions	DevOps
Security vulnerabilities	Średnie	Wysokie	Security scanning, penetration testing	Security Lead
Ryzyka biznesowe
Ryzyko	Prawdopodobieństwo	Impact	Mitigacja	Owner
Niższa adopcja niż zakładana	Średnie	Wysokie	Intensive training, user feedback loops	Product Owner
ROI nie osiągnięty	Niskie	Wysokie	Conservative projections, pilot program	Business Lead
Konkurencja z nowym produktem	Średnie	Średnie	Unique value prop, customer lock-in	Product Strategy
Zmiana regulacji środowiskowych	Niskie	Średnie	Regulatory monitoring, compliance buffer	Compliance Officer
Klient rezygnuje z on-premise	Niskie	Wysokie	Cloud-ready architecture, hybrid option	CTO
Ryzyka projektowe
Ryzyko	Prawdopodobieństwo	Impact	Mitigacja	Owner
Opóźnienie w dostawie	Średnie	Wysokie	Agile milestones, buffer time	Project Manager
Key person risk	Średnie	Wysokie	Knowledge sharing, documentation	Tech Lead
Scope creep	Wysokie	Średnie	Strict change management, MVP focus	Product Owner
Integration complexity	Średnie	Średnie	Proof of concepts, early integration	Solution Architect
Performance issues in prod	Średnie	Wysokie	Load testing, performance monitoring	Performance Engineer
Risk Monitoring Dashboard
json
{
  "technical_risks": {
    "algorithm_convergence_rate": 0.97,
    "average_optimization_time": 95,
    "data_validation_success_rate": 0.94,
    "system_availability": 0.998
  },
  "business_risks": {
    "user_adoption_rate": 0.73,
    "projected_roi_months": 16.2,
    "customer_satisfaction_nps": 8.1,
    "support_ticket_rate": 0.03
  },
  "project_risks": {
    "sprint_velocity": 85,
    "team_capacity": 0.90,
    "scope_change_requests": 3,
    "integration_test_pass_rate": 0.89
  }
}
Definition of Done
Story Definition of Done
Funkcjonalność jest gotowa gdy:

 Requirements: User story spełnia wszystkie kryteria akceptacji

 Development: Kod zaimplementowany zgodnie z coding standards

 Testing: Unit tests ≥80% coverage, integration tests passed

 Code Review: Peer review completed, all comments resolved

 Documentation: Code commented, API docs updated

 QA: Manual testing completed, edge cases verified

 Security: Security review dla sensitive functionality

 Performance: Performance requirements met and verified

 UX: UI/UX reviewed and approved by design team

 Deployment: Deployable to staging environment

 Demo: Feature demonstrated to Product Owner

 Monitoring: Metrics and logging implemented

Sprint Definition of Done
Sprint jest ukończony gdy:

 All Stories: Wszystkie story w sprint backlog completed

 Sprint Goal: Sprint goal achieved and measurable

 Testing: All automated tests passing (unit, integration, e2e)

 Performance: Performance benchmarks met

 Security: Security tests passed, no critical vulnerabilities

 Documentation: Sprint documentation updated

 Deployment: Code deployed to staging and tested

 Demo: Sprint demo prepared and delivered

 Retrospective: Sprint retrospective conducted

 Backlog: Next sprint backlog refined and ready

Release Definition of Done
Release jest gotowy gdy:

 Functionality: All MVP features implemented and tested

 Quality: Code quality gates passed (coverage, complexity, duplication)

 Performance: All performance SLOs met in production-like environment

 Security: Security scan passed, penetration testing completed

 UAT: User Acceptance Testing completed and signed off

 Documentation: User documentation, admin guides, API docs complete

 Training: Training materials prepared, team trained

 Operations: Monitoring, alerting, runbooks ready

 Compliance: All compliance requirements satisfied

 Backup/Recovery: Disaster recovery tested and documented

 Go-Live: Go-live checklist completed, rollback plan ready

 Support: Support team trained, escalation procedures ready

Plan UAT
UAT Scope i cele
Cele testowania:

Walidacja że system spełnia wymagania biznesowe

Potwierdzenie użyteczności dla użytkowników końcowych

Weryfikacja integracji z istniejącymi procesami

Akceptacja wydajności w warunkach produkcyjnych

UAT Environment
Wymagania środowiska:

Infrastructure: Production-like environment (same specs)

Data: Anonymized production data + synthetic test cases

Users: 5 engineers, 2 UTR specialists, 1 manager, 1 admin

Duration: 4 tygodnie testing + 1 tydzień retesting

Schedule: Phase 1 (Core functionality), Phase 2 (Advanced features)

UAT Test Scenarios
Scenario ID	Opis	User Role	Priority	Expected Duration
UAT-001	End-to-end workflow: Import → Configure → Optimize → Report	Engineer	Critical	2 hours
UAT-002	Bulk import 1000+ materials with validation errors	Engineer	High	45 min
UAT-003	Parallel optimization of 5 scenarios	Engineer	High	1 hour
UAT-004	Executive report generation and email delivery	Manager	High	30 min
UAT-005	User management and RBAC permissions	Admin	Critical	1 hour
UAT-006	System monitoring and alerting	Admin	Medium	45 min
UAT-007	Mobile/tablet viewing of reports	Manager	Low	30 min
UAT-008	Data export and external system integration	UTR Specialist	High	45 min
UAT-009	Error handling and recovery scenarios	Engineer	High	1 hour
UAT-010	Performance under load (25 concurrent users)	All Users	Critical	2 hours
UAT Success Criteria
Acceptance thresholds:

Functionality: 95% test scenarios pass without blocking issues

Usability: 80% users complete tasks without assistance

Performance: All SLOs met under realistic load

Reliability: Zero data loss, <1% transaction failures

Business Value: Users confirm 50%+ time savings vs current process

UAT Exit Criteria
UAT może zostać zakończone gdy:

Pass Rate: ≥95% test scenarios passed

Critical Issues: Zero critical issues open

High Issues: <5 high priority issues (with agreed workarounds)

User Acceptance: ≥90% user satisfaction score

Performance: All performance KPIs met

Documentation: All user-facing documentation approved

Training: All users trained and confident

Go-Live Readiness: Production environment ready

Support: Support team ready and trained

Sign-off: Formal business sign-off obtained

UAT Deliverables
UAT Test Plan: Detailed test scenarios and procedures

Test Results Report: Pass/fail status, defects found

User Feedback Report: Usability findings, improvement suggestions

Performance Test Report: Load testing results, bottlenecks

Business Sign-off: Formal acceptance document

Go-Live Readiness Assessment: Final readiness checklist

Słownik pojęć
Termin	Definicja
Regenerator	Urządzenie wymiany ciepła składające się z ogniotrwałej murki (checker)
Checker/Checkerpack	Ułożenie cegieł tworzące kanały dla przepływu gazów spalinowych i powietrza
U-value	Współczynnik przenikania ciepła [W/m²K], miara izolacyjności
Q_wall	Strumień ciepła przenikający przez ścianę [W]
NTU	Number of Transfer Units - bezwymiarowa miara efektywności wymiennika
LMTD	Logarithmic Mean Temperature Difference [K]
Fouling	Zanieczyszczenie powierzchni wymiany ciepła wpływające na wydajność
Δp (Delta-P)	Spadek ciśnienia w kanałach regeneratora [Pa]
SLSQP	Sequential Least Squares Programming - algorytm optymalizacji nieliniowej
Thermal efficiency	Stosunek ciepła użytecznego do ciepła dostarczonego [%]
Heat recovery	Odzysk ciepła z gazów spalinowych do podgrzania powietrza spalania
Crown regenerator	Typ regeneratora umieszczony nad piecem (top-fired)
End-port regenerator	Regenerator umieszczony na końcu pieca (end-fired)
Cross-fired	Konfiguracja z regeneratorami po bokach pieca
Refractory	Materiał ogniotrwały odporny na wysokie temperatury
SSE	Server-Sent Events - technologia real-time communication
RBAC	Role-Based Access Control - kontrola dostępu oparta na rolach
On-premise	Uruchomienie w lokalnej infrastrukturze klienta
MVP	Minimum Viable Product - podstawowa wersja produktu
SLO	Service Level Objective - cel poziomu usługi
KPI	Key Performance Indicator - kluczowy wskaźnik wydajności
Changelog
[1.0.0] - 2025-09-23
Added
Product Vision: Complete product requirements for Forglass Regenerator Optimizer

User Analysis: 4 detailed personas with 12 user stories (Given/When/Then format)

MVP Scope: 6 core modules with acceptance criteria and KPIs

User Flows: 3 detailed Mermaid flowcharts for key workflows

Functional Requirements: 20 detailed requirements with priorities and metrics

Non-Functional Requirements: Performance, security, reliability, and usability specs

Reports & Exports: Executive PDF and technical XLSX export specifications

Data Integration: Import/export formats, conversion rules, API contracts

KPIs & SLOs: Business and technical metrics with targets and alert thresholds

Risk Management: 15 identified risks with mitigations and owners

Definition of Done: Story/Sprint/Release checklists

UAT Plan: 4-week testing plan with 10 scenarios and success criteria

Business Requirements
Target: 5-15% fuel savings, <18 month ROI

Users: Engineers, UTR/Automatyk, Managers, Admins

Core Value: Reduce CO₂ emissions, increase efficiency, ensure auditability

Deployment: 100% on-premise with enterprise security

Technical Specifications
Performance: <2 min optimization, 99.5% availability, <200ms API response

Security: JWT + RBAC + TLS 1.3 + audit logging

Scalability: 50 concurrent users, 10 parallel optimizations

Integration: XLSX import/export, PDF reports, email notifications