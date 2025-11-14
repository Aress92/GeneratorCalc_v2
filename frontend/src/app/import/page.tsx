'use client';

/**
 * Import wizard page - Module 1 MVP implementation.
 *
 * Kreator importu danych XLSX z walidacją i podglądem.
 */

import { useState } from 'react';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import { hasPermission } from '@/lib/auth';
import { ImportAPI } from '@/lib/api-client';
// TODO: Re-enable sonner after fixing pnpm installation
// import { toast } from 'sonner';

// Temporary toast fallback until sonner is installed
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
  info: (msg: string) => console.info('ℹ️', msg),
};

function ImportPage() {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [columnMapping, setColumnMapping] = useState<any[]>([]);
  const [isDryRunLoading, setIsDryRunLoading] = useState(false);
  const [dryRunResult, setDryRunResult] = useState<any>(null);
  const [isImporting, setIsImporting] = useState(false);

  if (!user || !hasPermission(user, 'engineer')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Brak uprawnień</h2>
          <p className="text-gray-600">Nie masz uprawnień do importu danych.</p>
        </div>
      </div>
    );
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0 && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleFileSelect = async (file: File) => {
    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      toast.error('Tylko pliki Excel (.xlsx, .xls) są obsługiwane');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Plik jest zbyt duży. Maksymalny rozmiar to 10MB');
      return;
    }

    setSelectedFile(file);
    setCurrentStep(2);

    // Auto-preview file
    await previewFile(file);
  };

  const previewFile = async (file: File) => {
    setIsPreviewLoading(true);

    try {
      const data = await ImportAPI.previewFile(file);
      setPreviewData(data);

      // Initialize column mapping with suggested mappings
      if (data.suggested_mapping) {
        setColumnMapping(data.suggested_mapping);
      }

      setCurrentStep(3);
    } catch (error) {
      console.error('Preview error:', error);
      toast.error('Błąd podczas przetwarzania pliku');
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const resetWizard = () => {
    setCurrentStep(1);
    setSelectedFile(null);
    setPreviewData(null);
    setColumnMapping([]);
    setDryRunResult(null);
  };

  const updateColumnMapping = (sourceColumn: string, targetField: string, dataType: string = 'string', unit?: string) => {
    setColumnMapping(prev => {
      const updated = prev.map(mapping =>
        mapping.source_column === sourceColumn
          ? { ...mapping, target_field: targetField, data_type: dataType, unit }
          : mapping
      );

      // Add new mapping if not found
      if (!updated.find(m => m.source_column === sourceColumn)) {
        updated.push({
          source_column: sourceColumn,
          target_field: targetField,
          data_type: dataType,
          unit,
          is_required: false
        });
      }

      return updated;
    });
  };

  const performDryRun = async () => {
    if (!selectedFile) return;

    setIsDryRunLoading(true);
    try {
      const result = await ImportAPI.dryRun(
        selectedFile,
        previewData.detected_type || 'regenerator_config',
        columnMapping
      );
      setDryRunResult(result);
      setCurrentStep(5);
    } catch (error) {
      console.error('Dry run error:', error);
      toast.error('Błąd podczas testowego importu');
    } finally {
      setIsDryRunLoading(false);
    }
  };

  const performActualImport = async () => {
    if (!selectedFile) return;

    setIsImporting(true);
    try {
      const jobData = {
        original_filename: selectedFile.name,
        import_type: previewData.detected_type || 'regenerator_config',
        column_mapping: columnMapping,
        processing_options: {}
      };

      const result = await ImportAPI.createJob(selectedFile, jobData);
      toast.success(`Import uruchomiony pomyślnie! Job ID: ${result.id}`);

      // Redirect to job monitoring or dashboard
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Import error:', error);
      toast.error('Błąd podczas uruchamiania importu');
    } finally {
      setIsImporting(false);
    }
  };

  const downloadTemplate = async (templateType: string) => {
    try {
      // This would typically call ImportAPI.getTemplates() and then download
      // For now, we'll create a simple CSV template
      const csvData = templateType === 'regenerator_config'
        ? 'name,length,width,height,wall_thickness,material_type,gas_temp_inlet,gas_temp_outlet,mass_flow_rate\nSample Regenerator,10,8,6,0.4,firebrick,1600,600,50'
        : 'name,description,type\nSample,Sample description,crown';

      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${templateType}_template.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download template:', error);
      toast.error('Nie udało się pobrać szablonu');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <a href="/dashboard" className="text-blue-600 hover:text-blue-500 mr-4">
                ← Powrót do dashboardu
              </a>
              <h1 className="text-xl font-semibold text-gray-900">
                Import danych XLSX
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user.full_name || user.username}</span>
              <div className="text-sm text-gray-500">
                Krok {currentStep} z 5
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {[1, 2, 3, 4, 5].map((step, index) => (
              <div key={step} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full border-2 text-sm font-medium ${
                    step <= currentStep
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : 'bg-white border-gray-300 text-gray-500'
                  }`}
                >
                  {step}
                </div>
                {index < 4 && (
                  <div
                    className={`w-16 h-0.5 ${
                      step < currentStep ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-2">
            <div className="text-sm text-gray-600 text-center">
              {currentStep === 1 && "Wybierz plik"}
              {currentStep === 2 && "Przetwarzanie..."}
              {currentStep === 3 && "Podgląd i walidacja"}
              {currentStep === 4 && "Mapowanie kolumn"}
              {currentStep === 5 && "Finalizacja importu"}
            </div>
          </div>
        </div>

        <div className="px-4 py-6 sm:px-0">
          {/* Step 1: File Upload */}
          {currentStep === 1 && (
            <div className="max-w-3xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  Wybierz plik XLSX do importu
                </h2>

                {/* Drag & Drop Area */}
                <div
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    dragOver
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-gray-300 bg-gray-50'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 mb-4"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Przeciągnij plik tutaj lub kliknij aby wybrać
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Obsługiwane formaty: .xlsx, .xls (maksymalnie 10MB)
                  </p>
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
                  >
                    Wybierz plik
                  </label>
                </div>

                {/* Supported Templates */}
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Szablony do pobrania:
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <h4 className="font-medium text-gray-900 mb-2">Konfiguracja regeneratora</h4>
                      <p className="text-sm text-gray-600 mb-3">Parametry geometryczne i termiczne regeneratorów</p>
                      <button
                        onClick={() => downloadTemplate('regenerator_config')}
                        className="w-full px-3 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 text-sm font-medium"
                      >
                        Pobierz szablon CSV
                      </button>
                    </div>
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow opacity-60">
                      <h4 className="font-medium text-gray-900 mb-2">Właściwości materiałów</h4>
                      <p className="text-sm text-gray-600 mb-3">Katalog materiałów ogniotrwałych</p>
                      <button
                        disabled
                        className="w-full px-3 py-2 bg-gray-100 text-gray-400 rounded-md text-sm font-medium cursor-not-allowed"
                      >
                        Wkrótce dostępne
                      </button>
                    </div>
                    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow opacity-60">
                      <h4 className="font-medium text-gray-900 mb-2">Warunki eksploatacyjne</h4>
                      <p className="text-sm text-gray-600 mb-3">Parametry operacyjne i wydajnościowe</p>
                      <button
                        disabled
                        className="w-full px-3 py-2 bg-gray-100 text-gray-400 rounded-md text-sm font-medium cursor-not-allowed"
                      >
                        Wkrótce dostępne
                      </button>
                    </div>
                  </div>

                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">💡 Wskazówki:</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• Pobierz szablon i uzupełnij go swoimi danymi</li>
                      <li>• Zachowaj nagłówki kolumn (pierwszy wiersz)</li>
                      <li>• Zapisz plik jako .xlsx przed przesłaniem</li>
                      <li>• Sprawdź jednostki miar - system obsługuje konwersje automatyczne</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Processing */}
          {currentStep === 2 && (
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  Przetwarzanie pliku...
                </h2>
                <p className="text-gray-600">
                  Analizujemy strukturę danych i generujemy podgląd
                </p>
                {selectedFile && (
                  <div className="mt-4 text-sm text-gray-500">
                    Plik: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 3: Preview & Validation */}
          {currentStep === 3 && previewData && (
            <div className="max-w-6xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    Podgląd danych
                  </h2>
                  <button
                    onClick={resetWizard}
                    className="text-gray-600 hover:text-gray-800"
                  >
                    Wybierz inny plik
                  </button>
                </div>

                {/* File Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900">Wykryty typ</h3>
                    <p className="text-blue-600">{previewData.detected_type || 'Unknown'}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900">Liczba wierszy</h3>
                    <p className="text-green-600">{previewData.total_rows}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900">Kolumny</h3>
                    <p className="text-purple-600">{previewData.headers?.length || 0}</p>
                  </div>
                </div>

                {/* Validation Errors */}
                {previewData.validation_errors && previewData.validation_errors.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-medium text-red-600 mb-2">
                      Błędy walidacji ({previewData.validation_errors.length})
                    </h3>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      {previewData.validation_errors.slice(0, 5).map((error: any, index: number) => (
                        <div key={index} className="text-sm text-red-700 mb-1">
                          • {error.message || error}
                        </div>
                      ))}
                      {previewData.validation_errors.length > 5 && (
                        <div className="text-sm text-red-600 mt-2">
                          ... i {previewData.validation_errors.length - 5} więcej
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Data Preview Table */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Podgląd danych (pierwsze 10 wierszy)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {previewData.headers?.map((header: string, index: number) => (
                            <th
                              key={index}
                              className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {previewData.sample_rows?.slice(0, 10).map((row: any[], rowIndex: number) => (
                          <tr key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <td
                                key={cellIndex}
                                className="px-3 py-2 whitespace-nowrap text-sm text-gray-900"
                              >
                                {cell?.toString() || ''}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-between">
                  <button
                    onClick={resetWizard}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Anuluj
                  </button>
                  <button
                    onClick={() => setCurrentStep(4)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    disabled={previewData.validation_errors?.some((e: any) => e.severity === 'error')}
                  >
                    Przejdź do mapowania kolumn →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Column Mapping */}
          {currentStep === 4 && previewData && (
            <div className="max-w-6xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Mapowanie kolumn
                </h2>
                <p className="text-gray-600 mb-6">
                  Połącz kolumny z pliku z polami docelowymi w systemie. System automatycznie zasugerował mapowanie na podstawie nazw kolumn.
                </p>

                {/* Column Mapping Table */}
                <div className="overflow-x-auto mb-6">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Kolumna źródłowa
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Pole docelowe
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Typ danych
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Jednostka
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {previewData.headers?.map((header: string, index: number) => {
                        const mapping = columnMapping.find(m => m.source_column === header) || {
                          source_column: header,
                          target_field: 'unmapped',
                          data_type: 'string',
                          unit: '',
                          is_required: false
                        };

                        return (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {header}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <select
                                value={mapping.target_field}
                                onChange={(e) => updateColumnMapping(header, e.target.value, mapping.data_type, mapping.unit)}
                                className="block w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                              >
                                <option value="unmapped">--- Nie mapuj ---</option>
                                <option value="name">Nazwa</option>
                                <option value="description">Opis</option>
                                <option value="regenerator_type">Typ regeneratora</option>
                                <option value="length">Długość</option>
                                <option value="width">Szerokość</option>
                                <option value="height">Wysokość</option>
                                <option value="design_temperature">Temperatura projektowa</option>
                                <option value="max_temperature">Temperatura maksymalna</option>
                                <option value="working_pressure">Ciśnienie robocze</option>
                                <option value="air_flow_rate">Przepływ powietrza</option>
                                <option value="gas_flow_rate">Przepływ gazu</option>
                                <option value="pressure_drop">Spadek ciśnienia</option>
                                <option value="checker_material">Materiał checker</option>
                                <option value="insulation_material">Materiał izolacji</option>
                                <option value="refractory_material">Materiał ogniotrwały</option>
                                <option value="thermal_efficiency">Sprawność termiczna</option>
                                <option value="heat_recovery_rate">Stopień odzysku ciepła</option>
                                <option value="fuel_consumption">Zużycie paliwa</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <select
                                value={mapping.data_type}
                                onChange={(e) => updateColumnMapping(header, mapping.target_field, e.target.value, mapping.unit)}
                                className="block w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                disabled={mapping.target_field === 'unmapped'}
                              >
                                <option value="string">Tekst</option>
                                <option value="float">Liczba dziesiętna</option>
                                <option value="integer">Liczba całkowita</option>
                                <option value="boolean">Tak/Nie</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <input
                                type="text"
                                value={mapping.unit || ''}
                                onChange={(e) => updateColumnMapping(header, mapping.target_field, mapping.data_type, e.target.value)}
                                placeholder="np. m, °C, Pa"
                                className="block w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                disabled={mapping.target_field === 'unmapped' || mapping.data_type === 'string'}
                              />
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                mapping.target_field === 'unmapped'
                                  ? 'bg-gray-100 text-gray-800'
                                  : mapping.is_required
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {mapping.target_field === 'unmapped'
                                  ? 'Pominięte'
                                  : mapping.is_required
                                  ? 'Wymagane'
                                  : 'Opcjonalne'
                                }
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Mapping Summary */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Podsumowanie mapowania:</h3>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Zmapowane kolumny:</span>
                      <span className="ml-2 text-green-600">
                        {columnMapping.filter(m => m.target_field !== 'unmapped').length}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Pominięte kolumny:</span>
                      <span className="ml-2 text-gray-600">
                        {columnMapping.filter(m => m.target_field === 'unmapped').length}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Wymagane pola:</span>
                      <span className="ml-2 text-red-600">
                        {columnMapping.filter(m => m.is_required).length}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-between">
                  <button
                    onClick={() => setCurrentStep(3)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    ← Wstecz do podglądu
                  </button>
                  <div className="space-x-3">
                    <button
                      onClick={performDryRun}
                      disabled={isDryRunLoading}
                      className="px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 disabled:opacity-50"
                    >
                      {isDryRunLoading ? 'Testowanie...' : 'Test importu'}
                    </button>
                    <button
                      onClick={() => setCurrentStep(5)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Przejdź do finalizacji →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 5: Finalization & Dry Run Results */}
          {currentStep === 5 && (
            <div className="max-w-6xl mx-auto">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  Finalizacja importu
                </h2>

                {/* Dry Run Results */}
                {dryRunResult && (
                  <div className="mb-8">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">
                      Wyniki testowego importu
                    </h3>

                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-blue-900">Wszystkich wierszy</h4>
                        <p className="text-2xl font-bold text-blue-600">{dryRunResult.summary?.total_rows || 0}</p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-green-900">Poprawnych</h4>
                        <p className="text-2xl font-bold text-green-600">{dryRunResult.summary?.valid_rows || 0}</p>
                      </div>
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-red-900">Błędnych</h4>
                        <p className="text-2xl font-bold text-red-600">{dryRunResult.summary?.invalid_rows || 0}</p>
                      </div>
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-yellow-900">Skuteczność</h4>
                        <p className="text-2xl font-bold text-yellow-600">{dryRunResult.summary?.success_rate || 0}%</p>
                      </div>
                    </div>

                    {/* Recommendations */}
                    {dryRunResult.recommendations && dryRunResult.recommendations.length > 0 && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                        <h4 className="text-sm font-medium text-blue-900 mb-2">Zalecenia:</h4>
                        <ul className="text-sm text-blue-800 space-y-1">
                          {dryRunResult.recommendations.map((rec: string, index: number) => (
                            <li key={index}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Validation Errors */}
                    {dryRunResult.validation?.errors && dryRunResult.validation.errors.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-sm font-medium text-red-900 mb-2">
                          Błędy walidacji ({dryRunResult.validation.error_count})
                        </h4>
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-h-48 overflow-y-auto">
                          {dryRunResult.validation.errors.slice(0, 10).map((error: any, index: number) => (
                            <div key={index} className="text-sm text-red-700 mb-1">
                              Wiersz {error.row}: {error.message}
                            </div>
                          ))}
                          {dryRunResult.validation.error_count > 10 && (
                            <div className="text-sm text-red-600 mt-2">
                              ... i {dryRunResult.validation.error_count - 10} więcej błędów
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Sample Valid Data */}
                    {dryRunResult.samples?.valid_data && dryRunResult.samples.valid_data.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-sm font-medium text-green-900 mb-2">
                          Przykłady poprawnych danych
                        </h4>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                          {dryRunResult.samples.valid_data.slice(0, 3).map((sample: any, index: number) => (
                            <div key={index} className="text-sm text-green-700 mb-2">
                              <strong>Wiersz {sample.row}:</strong> {sample.data.name || 'Brak nazwy'}
                              {sample.warnings && sample.warnings.length > 0 && (
                                <div className="ml-4 text-yellow-600">
                                  Ostrzeżenia: {sample.warnings.join(', ')}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Import Summary */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Podsumowanie importu</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p><strong>Plik:</strong> {selectedFile?.name}</p>
                      <p><strong>Rozmiar:</strong> {selectedFile ? (selectedFile.size / 1024 / 1024).toFixed(2) : 0} MB</p>
                      <p><strong>Typ importu:</strong> {previewData?.detected_type || 'regenerator_config'}</p>
                    </div>
                    <div>
                      <p><strong>Zmapowane kolumny:</strong> {columnMapping.filter(m => m.target_field !== 'unmapped').length}</p>
                      <p><strong>Przewidywana skuteczność:</strong> {dryRunResult?.summary?.success_rate || 'N/A'}%</p>
                      <p><strong>Szacowany czas:</strong> {selectedFile && previewData ? Math.ceil(previewData.total_rows / 100) : 'N/A'} sekund</p>
                    </div>
                  </div>
                </div>

                {/* Final Actions */}
                <div className="flex justify-between items-center">
                  <div className="space-x-3">
                    <button
                      onClick={() => setCurrentStep(4)}
                      className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                    >
                      ← Wstecz do mapowania
                    </button>
                    <button
                      onClick={performDryRun}
                      disabled={isDryRunLoading}
                      className="px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 disabled:opacity-50"
                    >
                      {isDryRunLoading ? 'Testowanie...' : 'Powtórz test'}
                    </button>
                  </div>

                  <div className="text-center">
                    {dryRunResult?.summary?.success_rate && dryRunResult.summary.success_rate < 80 && (
                      <div className="text-sm text-yellow-600 mb-2">
                        ⚠️ Niska skuteczność importu. Rozważ poprawienie danych.
                      </div>
                    )}

                    <button
                      onClick={performActualImport}
                      disabled={isImporting || (dryRunResult?.summary?.success_rate && dryRunResult.summary.success_rate < 50)}
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                    >
                      {isImporting ? (
                        <span className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Importowanie...
                        </span>
                      ) : (
                        'Uruchom import 🚀'
                      )}
                    </button>
                  </div>

                  <div className="space-x-3">
                    <button
                      onClick={resetWizard}
                      className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                    >
                      Nowy import
                    </button>
                    <a
                      href="/dashboard"
                      className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                    >
                      Dashboard
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default withAuth(ImportPage);