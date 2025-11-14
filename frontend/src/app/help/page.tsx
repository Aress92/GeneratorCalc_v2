'use client';

import { useState } from 'react';
import {
  BookOpen, ChevronDown, ChevronRight, Search, Home,
  Settings, Play, BarChart, Database, FileText, AlertCircle,
  CheckCircle, Clock, XCircle, Info
} from 'lucide-react';

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['intro']));

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const expandAll = () => {
    setExpandedSections(new Set([
      'intro', 'login', 'dashboard', 'configurations', 'scenarios',
      'running', 'monitoring', 'results', 'materials', 'reports', 'troubleshooting'
    ]));
  };

  const collapseAll = () => {
    setExpandedSections(new Set());
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dokumentacja Użytkownika</h1>
                <p className="text-sm text-gray-500 mt-1">Forglass Regenerator Optimizer v1.0</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={expandAll}
                className="px-4 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
              >
                Rozwiń wszystko
              </button>
              <button
                onClick={collapseAll}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Zwiń wszystko
              </button>
            </div>
          </div>

          {/* Search */}
          <div className="mt-6 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Szukaj w dokumentacji..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

          {/* Sidebar - Table of Contents */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-8">
              <h3 className="font-semibold text-gray-900 mb-4">Spis treści</h3>
              <nav className="space-y-2 text-sm">
                <a href="#intro" className="block text-blue-600 hover:text-blue-800">Wprowadzenie</a>
                <a href="#login" className="block text-gray-600 hover:text-gray-900">Logowanie</a>
                <a href="#dashboard" className="block text-gray-600 hover:text-gray-900">Dashboard</a>
                <a href="#configurations" className="block text-gray-600 hover:text-gray-900">Konfiguracje</a>
                <a href="#scenarios" className="block text-gray-600 hover:text-gray-900">Scenariusze</a>
                <a href="#running" className="block text-gray-600 hover:text-gray-900">Uruchamianie</a>
                <a href="#monitoring" className="block text-gray-600 hover:text-gray-900">Monitorowanie</a>
                <a href="#results" className="block text-gray-600 hover:text-gray-900">Wyniki</a>
                <a href="#materials" className="block text-gray-600 hover:text-gray-900">Materiały</a>
                <a href="#reports" className="block text-gray-600 hover:text-gray-900">Raporty</a>
                <a href="#troubleshooting" className="block text-gray-600 hover:text-gray-900">Problemy</a>
              </nav>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Potrzebujesz pomocy?</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>📧 support@forglass.com</p>
                  <p>📞 +48 XX XXX XXXX</p>
                  <p className="text-xs text-gray-400 mt-2">PN-PT: 8:00-16:00</p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">

            {/* Wprowadzenie */}
            <Section
              id="intro"
              title="Wprowadzenie"
              icon={<Home className="w-5 h-5" />}
              expanded={expandedSections.has('intro')}
              onToggle={() => toggleSection('intro')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  <strong>Forglass Regenerator Optimizer (FRO)</strong> to zaawansowany system do optymalizacji regeneratorów pieców szklarskich.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FeatureCard
                    icon="🔥"
                    title="Redukcja zużycia paliwa"
                    value="5-15%"
                  />
                  <FeatureCard
                    icon="🌱"
                    title="Obniżenie emisji CO₂"
                    value="5-15%"
                  />
                  <FeatureCard
                    icon="💰"
                    title="Oszczędności roczne"
                    value="do $357,000"
                  />
                  <FeatureCard
                    icon="📊"
                    title="Czas symulacji"
                    value="30-60 sekund"
                  />
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                  <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <Info className="w-5 h-5" />
                    Wymagania systemowe
                  </h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Przeglądarka: Chrome 90+, Firefox 88+, Edge 90+</li>
                    <li>• Rozdzielczość: minimum 1366x768</li>
                    <li>• Połączenie: stabilne (do synchronizacji danych)</li>
                  </ul>
                </div>
              </div>
            </Section>

            {/* Logowanie */}
            <Section
              id="login"
              title="Logowanie do systemu"
              icon={<Settings className="w-5 h-5" />}
              expanded={expandedSections.has('login')}
              onToggle={() => toggleSection('login')}
            >
              <div className="space-y-4">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Pierwsze logowanie</h4>
                  <ol className="space-y-2 text-sm text-gray-700">
                    <li>1. Otwórz: <code className="bg-white px-2 py-1 rounded border">http://localhost:3000</code></li>
                    <li>2. Użytkownik: <code className="bg-white px-2 py-1 rounded border">admin</code></li>
                    <li>3. Hasło: <code className="bg-white px-2 py-1 rounded border">admin</code></li>
                    <li>4. Kliknij <strong>"Zaloguj"</strong></li>
                  </ol>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Ważne!
                  </h4>
                  <p className="text-sm text-amber-800">
                    Po pierwszym logowaniu koniecznie zmień hasło administratora w ustawieniach profilu!
                  </p>
                </div>

                <table className="w-full text-sm border-collapse">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="border border-gray-200 px-4 py-2 text-left">Rola</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Uprawnienia</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2 font-medium">ADMIN</td>
                      <td className="border border-gray-200 px-4 py-2">Pełny dostęp, zarządzanie użytkownikami</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2 font-medium">ENGINEER</td>
                      <td className="border border-gray-200 px-4 py-2">Tworzenie i uruchamianie optymalizacji</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2 font-medium">VIEWER</td>
                      <td className="border border-gray-200 px-4 py-2">Tylko podgląd wyników</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Section>

            {/* Dashboard */}
            <Section
              id="dashboard"
              title="Dashboard - Centrum kontrolne"
              icon={<BarChart className="w-5 h-5" />}
              expanded={expandedSections.has('dashboard')}
              onToggle={() => toggleSection('dashboard')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  Dashboard wyświetla kluczowe metryki i status systemu w czasie rzeczywistym.
                </p>

                <div className="grid grid-cols-2 gap-4">
                  <MetricCard title="Aktywne optymalizacje" value="3" color="blue" />
                  <MetricCard title="Ukończone dzisiaj" value="12" color="green" />
                  <MetricCard title="Średnia efektywność" value="94.5%" color="purple" />
                  <MetricCard title="Oszczędności CO₂" value="2,450 kg" color="emerald" />
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Dostępne funkcje</h4>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li>• 📊 Wykresy efektywności w czasie</li>
                    <li>• 📈 Porównanie konfiguracji (baseline vs. optymalizowane)</li>
                    <li>• 🔍 Status systemów (Backend, Celery, Redis, MySQL)</li>
                    <li>• 🚀 Szybki start nowej optymalizacji</li>
                    <li>• 📄 Ostatnie wyniki i raporty</li>
                  </ul>
                </div>
              </div>
            </Section>

            {/* Scenariusze */}
            <Section
              id="scenarios"
              title="Scenariusze optymalizacji"
              icon={<Play className="w-5 h-5" />}
              expanded={expandedSections.has('scenarios')}
              onToggle={() => toggleSection('scenarios')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  <strong>Scenariusz</strong> definiuje parametry optymalizacji: cel, algorytm, zmienne projektowe i ograniczenia.
                </p>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-3">Cele optymalizacji</h4>
                  <div className="space-y-2 text-sm text-blue-800">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>🔥 Minimalizacja zużycia paliwa (domyślnie)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>🌱 Minimalizacja emisji CO₂</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>📈 Maksymalizacja efektywności termicznej</span>
                    </div>
                  </div>
                </div>

                <table className="w-full text-sm border-collapse">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="border border-gray-200 px-4 py-2 text-left">Zmienna</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Zakres</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Wpływ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2">Wysokość checkera</td>
                      <td className="border border-gray-200 px-4 py-2">0.5 - 3.0 m</td>
                      <td className="border border-gray-200 px-4 py-2">Czas kontaktu, powierzchnia</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2">Grubość ścianki</td>
                      <td className="border border-gray-200 px-4 py-2">0.1 - 1.0 m</td>
                      <td className="border border-gray-200 px-4 py-2">Straty ciepła, wytrzymałość</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-200 px-4 py-2">Rozstaw checkerów</td>
                      <td className="border border-gray-200 px-4 py-2">0.03 - 0.15 m</td>
                      <td className="border border-gray-200 px-4 py-2">Opory przepływu, efektywność</td>
                    </tr>
                  </tbody>
                </table>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-900 mb-2">💡 Wskazówka</h4>
                  <p className="text-sm text-green-800">
                    Zacznij od małej liczby iteracji (50-100) jako test, następnie zwiększ jeśli potrzeba większej dokładności.
                  </p>
                </div>
              </div>
            </Section>

            {/* Monitorowanie */}
            <Section
              id="monitoring"
              title="Monitorowanie postępów"
              icon={<Clock className="w-5 h-5" />}
              expanded={expandedSections.has('monitoring')}
              onToggle={() => toggleSection('monitoring')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  Śledź postęp optymalizacji w czasie rzeczywistym w zakładce <strong>"Zadania"</strong>.
                </p>

                <div className="space-y-3">
                  <StatusBadge status="pending" label="Pending" description="Oczekuje na wolny worker" />
                  <StatusBadge status="running" label="Running" description="Optymalizacja w toku" />
                  <StatusBadge status="completed" label="Completed" description="Zakończone sukcesem" />
                  <StatusBadge status="failed" label="Failed" description="Błąd podczas wykonania" />
                  <StatusBadge status="cancelled" label="Cancelled" description="Anulowane przez użytkownika" />
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-3">Pasek postępu zawiera</h4>
                  <ul className="space-y-2 text-sm text-blue-800">
                    <li>• Procent ukończenia (0-100%)</li>
                    <li>• Aktualna iteracja / Max iteracji</li>
                    <li>• Czas wykonania (elapsed time)</li>
                    <li>• Szacowany czas do końca (ETA)</li>
                  </ul>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Szacowany czas wykonania</h4>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• 10 iteracji: ~5-10 sekund</li>
                    <li>• 100 iteracji: ~30-60 sekund (zalecane)</li>
                    <li>• 1000 iteracji: ~5-10 minut (wysoka precyzja)</li>
                  </ul>
                </div>
              </div>
            </Section>

            {/* Wyniki */}
            <Section
              id="results"
              title="Przeglądanie wyników"
              icon={<BarChart className="w-5 h-5" />}
              expanded={expandedSections.has('results')}
              onToggle={() => toggleSection('results')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  Wyniki optymalizacji zawierają szczegółową analizę techniczną i ekonomiczną.
                </p>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <div className="text-xs text-blue-600 font-medium mb-1">Efektywność termiczna</div>
                    <div className="text-2xl font-bold text-blue-900">98.64%</div>
                    <div className="text-xs text-blue-700 mt-1">+7.15% vs baseline</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <div className="text-xs text-green-600 font-medium mb-1">Oszczędności roczne</div>
                    <div className="text-2xl font-bold text-green-900">$357,320</div>
                    <div className="text-xs text-green-700 mt-1">Okres zwrotu: 24 mies.</div>
                  </div>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    Interpretacja wyników
                  </h4>
                  <ul className="text-sm text-amber-800 space-y-1">
                    <li>• <strong>Feasibility &lt; 0.5</strong>: Rozwiązanie częściowo wykonalne, wymaga weryfikacji</li>
                    <li>• <strong>Confidence &lt; 0.5</strong>: Niska pewność - zwiększ liczbę iteracji</li>
                    <li>• <strong>Okres zwrotu &gt; 36 mies.</strong>: Inwestycja średnio opłacalna</li>
                    <li>• <strong>Okres zwrotu &lt; 24 mies.</strong>: Bardzo opłacalna inwestycja</li>
                  </ul>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Dostępne formaty eksportu</h4>
                  <div className="flex gap-3">
                    <div className="flex-1 bg-white border border-gray-200 rounded p-3 text-center">
                      <FileText className="w-6 h-6 text-red-500 mx-auto mb-2" />
                      <div className="text-sm font-medium">PDF</div>
                      <div className="text-xs text-gray-500">Raport techniczny</div>
                    </div>
                    <div className="flex-1 bg-white border border-gray-200 rounded p-3 text-center">
                      <FileText className="w-6 h-6 text-green-500 mx-auto mb-2" />
                      <div className="text-sm font-medium">Excel</div>
                      <div className="text-xs text-gray-500">Dane do analizy</div>
                    </div>
                    <div className="flex-1 bg-white border border-gray-200 rounded p-3 text-center">
                      <FileText className="w-6 h-6 text-blue-500 mx-auto mb-2" />
                      <div className="text-sm font-medium">JSON</div>
                      <div className="text-xs text-gray-500">Format surowych danych</div>
                    </div>
                  </div>
                </div>
              </div>
            </Section>

            {/* Materiały */}
            <Section
              id="materials"
              title="Baza materiałów"
              icon={<Database className="w-5 h-5" />}
              expanded={expandedSections.has('materials')}
              onToggle={() => toggleSection('materials')}
            >
              <div className="space-y-4">
                <p className="text-gray-700">
                  System zawiera <strong>111 materiałów ogniotrwałych</strong> z pełnymi danymi termicznymi.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Kategorie materiałów</h4>
                    <ul className="text-sm text-gray-700 space-y-1">
                      <li>• Cegły szamotowe (Fireclay)</li>
                      <li>• Cegły krzemionkowe (Silica)</li>
                      <li>• Cegły magnezytowe (Magnesia)</li>
                      <li>• Cegły chromowo-magnezytowe</li>
                      <li>• Materiały izolacyjne</li>
                      <li>• Betonony ogniotrwałe</li>
                    </ul>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Parametry materiałów</h4>
                    <ul className="text-sm text-gray-700 space-y-1">
                      <li>• Przewodność cieplna λ [W/(m·K)]</li>
                      <li>• Ciepło właściwe Cp [J/(kg·K)]</li>
                      <li>• Gęstość ρ [kg/m³]</li>
                      <li>• Maksymalna temperatura Tmax [°C]</li>
                      <li>• Odporność chemiczna</li>
                      <li>• Koszt orientacyjny [$/kg]</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">🔍 Wyszukiwanie i filtrowanie</h4>
                  <p className="text-sm text-blue-800">
                    Użyj pola wyszukiwania lub filtrów (kategoria, temperatura, koszt) aby szybko znaleźć odpowiedni materiał.
                  </p>
                </div>
              </div>
            </Section>

            {/* Rozwiązywanie problemów */}
            <Section
              id="troubleshooting"
              title="Rozwiązywanie problemów"
              icon={<AlertCircle className="w-5 h-5" />}
              expanded={expandedSections.has('troubleshooting')}
              onToggle={() => toggleSection('troubleshooting')}
            >
              <div className="space-y-4">
                <TroubleshootingItem
                  problem="Nie mogę się zalogować"
                  solutions={[
                    "Sprawdź czy używasz poprawnych danych: admin / admin",
                    "Wyczyść cookies przeglądarki (Ctrl+Shift+Delete)",
                    "Sprawdź czy backend działa: http://localhost:8000/health"
                  ]}
                />

                <TroubleshootingItem
                  problem="Zadanie utknęło w statusie Pending"
                  solutions={[
                    "Zaczekaj 1-2 minuty - może brak wolnych workers",
                    "Anuluj zadanie i uruchom ponownie",
                    "Sprawdź logi Celery (skontaktuj się z administratorem)"
                  ]}
                />

                <TroubleshootingItem
                  problem="Optymalizacja kończy się błędem Failed"
                  solutions={[
                    "Sprawdź komunikat błędu w szczegółach zadania",
                    "Zweryfikuj poprawność danych wejściowych (temperatury, przepływy)",
                    "Upewnij się że zakresy zmiennych są realistyczne",
                    "Jeśli problem się powtarza - zgłoś administratorowi"
                  ]}
                />

                <TroubleshootingItem
                  problem="Wyniki wyglądają nierealistycznie"
                  solutions={[
                    "Zbyt wysoka efektywność (>99%) - sprawdź dane wejściowe",
                    "Ujemne oszczędności - konfiguracja bazowa może być bliska optimum",
                    "Długi okres zwrotu (>60 mies.) - sprawdź koszty materiałów",
                    "Zwiększ liczbę iteracji dla lepszej precyzji"
                  ]}
                />

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-3">Kontakt z supportem</h4>
                  <div className="space-y-2 text-sm text-blue-800">
                    <p>📧 Email: <strong>support@forglass.com</strong></p>
                    <p>📞 Telefon: <strong>+48 XX XXX XXXX</strong></p>
                    <p className="text-xs text-blue-600">Godziny pracy: PN-PT 8:00-16:00</p>
                  </div>
                </div>
              </div>
            </Section>

          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              © 2025 Forglass Sp. z o.o. Wszystkie prawa zastrzeżone.
            </div>
            <div>
              Wersja 1.0 - MVP Production Ready
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Components
function Section({
  id,
  title,
  icon,
  children,
  expanded,
  onToggle
}: {
  id: string;
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div id={id} className="bg-white rounded-lg shadow-sm border border-gray-200">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="text-blue-600">{icon}</div>
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        </div>
        {expanded ? (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </button>
      {expanded && (
        <div className="px-6 pb-6 border-t border-gray-100">
          <div className="pt-6">{children}</div>
        </div>
      )}
    </div>
  );
}

function FeatureCard({ icon, title, value }: { icon: string; title: string; value: string }) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-sm text-gray-600 mb-1">{title}</div>
      <div className="text-xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

function MetricCard({ title, value, color }: { title: string; value: string; color: string }) {
  const colorClasses = {
    blue: 'from-blue-50 to-blue-100 border-blue-200 text-blue-900',
    green: 'from-green-50 to-green-100 border-green-200 text-green-900',
    purple: 'from-purple-50 to-purple-100 border-purple-200 text-purple-900',
    emerald: 'from-emerald-50 to-emerald-100 border-emerald-200 text-emerald-900',
  };

  return (
    <div className={`bg-gradient-to-br rounded-lg p-4 border ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="text-xs opacity-75 mb-1">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

function StatusBadge({ status, label, description }: { status: string; label: string; description: string }) {
  const statusConfig = {
    pending: { icon: <Clock className="w-5 h-5" />, color: 'border-yellow-200 bg-yellow-50 text-yellow-800' },
    running: { icon: <Play className="w-5 h-5" />, color: 'border-blue-200 bg-blue-50 text-blue-800' },
    completed: { icon: <CheckCircle className="w-5 h-5" />, color: 'border-green-200 bg-green-50 text-green-800' },
    failed: { icon: <XCircle className="w-5 h-5" />, color: 'border-red-200 bg-red-50 text-red-800' },
    cancelled: { icon: <XCircle className="w-5 h-5" />, color: 'border-gray-200 bg-gray-50 text-gray-800' },
  };

  const config = statusConfig[status as keyof typeof statusConfig];

  return (
    <div className={`flex items-center gap-3 border rounded-lg p-3 ${config.color}`}>
      {config.icon}
      <div className="flex-1">
        <div className="font-semibold">{label}</div>
        <div className="text-sm opacity-75">{description}</div>
      </div>
    </div>
  );
}

function TroubleshootingItem({ problem, solutions }: { problem: string; solutions: string[] }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <XCircle className="w-5 h-5 text-red-500" />
        {problem}
      </h4>
      <ul className="space-y-2 text-sm text-gray-700">
        {solutions.map((solution, index) => (
          <li key={index} className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
            <span>{solution}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
