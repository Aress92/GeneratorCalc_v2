'use client';

/**
 * Regenerator Configurator page - Module 2 MVP implementation.
 *
 * Kreator konfiguracji regeneratora z wizualizacją 3D.
 */

import { useState, useEffect } from 'react';
import { useAuth, withAuth } from '@/contexts/AuthContext';
import { hasPermission } from '@/lib/auth';
import { MaterialsAPI, RegeneratorsAPI } from '@/lib/api-client';

interface ConfigurationData {
  name: string;
  description: string;
  regenerator_type: 'crown' | 'end-port' | 'cross-fired';
  geometry: {
    length: number;
    width: number;
    height: number;
    checker_height: number;
  };
  materials: {
    checker_material_id: string;
    wall_material_id: string;
  };
  operating_conditions: {
    air_flow_rate: number;
    gas_flow_rate: number;
    air_inlet_temp: number;
    gas_inlet_temp: number;
    design_pressure: number;
  };
  thermal_properties: {
    target_efficiency: number;
    max_operating_temp: number;
    pressure_drop_limit: number;
  };
}

function ConfiguratorPage() {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [configData, setConfigData] = useState<ConfigurationData>({
    name: '',
    description: '',
    regenerator_type: 'crown',
    geometry: {
      length: 10.0,
      width: 8.0,
      height: 12.0,
      checker_height: 10.0,
    },
    materials: {
      checker_material_id: '',
      wall_material_id: '',
    },
    operating_conditions: {
      air_flow_rate: 25000,
      gas_flow_rate: 30000,
      air_inlet_temp: 200,
      gas_inlet_temp: 1450,
      design_pressure: 2500,
    },
    thermal_properties: {
      target_efficiency: 85.0,
      max_operating_temp: 1600,
      pressure_drop_limit: 5000,
    },
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [materials, setMaterials] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user && hasPermission(user, 'engineer')) {
      loadMaterials();
    }
  }, [user]);

  if (!user || !hasPermission(user, 'engineer')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Brak uprawnień</h2>
          <p className="text-gray-600">Nie masz uprawnień do konfiguracji regeneratorów.</p>
        </div>
      </div>
    );
  }

  const loadMaterials = async () => {
    try {
      const response = await MaterialsAPI.getMaterials({
        is_active: true,
        limit: 100
      });
      const materials = Array.isArray(response) ? response : (response as any)?.materials || [];
      setMaterials(materials);
    } catch (error) {
      console.error('Failed to load materials:', error);
    }
  };

  const validateCurrentStep = (): boolean => {
    const errors: string[] = [];

    switch (currentStep) {
      case 1: // Basic Info
        if (!configData.name.trim()) errors.push('Nazwa konfiguracji jest wymagana');
        if (configData.name.length > 255) errors.push('Nazwa nie może być dłuższa niż 255 znaków');
        break;

      case 2: // Regenerator Type
        if (!configData.regenerator_type) errors.push('Typ regeneratora jest wymagany');
        break;

      case 3: // Geometry
        if (configData.geometry.length <= 0) errors.push('Długość musi być większa od 0');
        if (configData.geometry.width <= 0) errors.push('Szerokość musi być większa od 0');
        if (configData.geometry.height <= 0) errors.push('Wysokość musi być większa od 0');
        if (configData.geometry.checker_height >= configData.geometry.height) {
          errors.push('Wysokość checkera musi być mniejsza niż wysokość regeneratora');
        }
        break;

      case 4: // Materials
        if (!configData.materials.checker_material_id) errors.push('Materiał checkera jest wymagany');
        if (!configData.materials.wall_material_id) errors.push('Materiał ściany jest wymagany');
        break;

      case 5: // Operating Conditions
        if (configData.operating_conditions.air_flow_rate <= 0) errors.push('Przepływ powietrza musi być większy od 0');
        if (configData.operating_conditions.gas_flow_rate <= 0) errors.push('Przepływ gazu musi być większy od 0');
        if (configData.operating_conditions.air_inlet_temp <= 0) errors.push('Temperatura wlotowa powietrza musi być większa od 0');
        if (configData.operating_conditions.gas_inlet_temp <= 0) errors.push('Temperatura wlotowa gazu musi być większa od 0');
        break;

      case 6: // Thermal Properties
        if (configData.thermal_properties.target_efficiency <= 0 || configData.thermal_properties.target_efficiency > 100) {
          errors.push('Docelowa sprawność musi być między 0 a 100%');
        }
        if (configData.thermal_properties.max_operating_temp <= 0) errors.push('Maksymalna temperatura musi być większa od 0');
        break;
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  const nextStep = () => {
    if (validateCurrentStep() && currentStep < 7) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const saveConfiguration = async () => {
    if (!validateCurrentStep()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/regenerators/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(configData),
      });

      if (response.ok) {
        alert('Konfiguracja została zapisana pomyślnie!');
        // Redirect to regenerators list or dashboard
        window.location.href = '/dashboard';
      } else {
        const error = await response.json();
        alert(`Błąd podczas zapisywania: ${error.detail}`);
      }
    } catch (error) {
      console.error('Save error:', error);
      alert('Wystąpił błąd podczas zapisywania konfiguracji');
    } finally {
      setIsLoading(false);
    }
  };

  const stepTitles = [
    'Podstawowe informacje',
    'Typ regeneratora',
    'Geometria',
    'Materiały',
    'Warunki pracy',
    'Właściwości termiczne',
    'Podsumowanie'
  ];

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
                Konfigurator regeneratora
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user.full_name || user.username}</span>
              <div className="text-sm text-gray-500">
                Krok {currentStep} z 7
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center">
            {[1, 2, 3, 4, 5, 6, 7].map((step, index) => (
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
                {index < 6 && (
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
              {stepTitles[currentStep - 1]}
            </div>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Main Configuration Panel */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-md p-8">
              {/* Validation Errors */}
              {validationErrors.length > 0 && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                  <h3 className="text-red-600 font-medium mb-2">Błędy walidacji:</h3>
                  <ul className="text-red-600 text-sm space-y-1">
                    {validationErrors.map((error, index) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Step 1: Basic Info */}
              {currentStep === 1 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Podstawowe informacje
                  </h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nazwa konfiguracji *
                      </label>
                      <input
                        type="text"
                        value={configData.name}
                        onChange={(e) => setConfigData({...configData, name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="np. Regenerator Crown Type A"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Opis (opcjonalny)
                      </label>
                      <textarea
                        value={configData.description}
                        onChange={(e) => setConfigData({...configData, description: e.target.value})}
                        rows={4}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Opis konfiguracji regeneratora..."
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Regenerator Type */}
              {currentStep === 2 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Typ regeneratora
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                      {
                        value: 'crown',
                        title: 'Crown Regenerator',
                        description: 'Regenerator umieszczony nad piecem (top-fired)',
                        features: ['Najczęściej używany', 'Dobra dostępność', 'Łatwy serwis']
                      },
                      {
                        value: 'end-port',
                        title: 'End-Port Regenerator',
                        description: 'Regenerator umieszczony na końcu pieca (end-fired)',
                        features: ['Kompaktowy design', 'Niższe koszty', 'Mniejsza powierzchnia']
                      },
                      {
                        value: 'cross-fired',
                        title: 'Cross-Fired Regenerator',
                        description: 'Regeneratory po bokach pieca',
                        features: ['Równomierne ogrzewanie', 'Wysoka wydajność', 'Złożony design']
                      }
                    ].map((type) => (
                      <div
                        key={type.value}
                        className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
                          configData.regenerator_type === type.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setConfigData({...configData, regenerator_type: type.value as any})}
                      >
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {type.title}
                        </h3>
                        <p className="text-gray-600 text-sm mb-4">
                          {type.description}
                        </p>
                        <ul className="text-sm text-gray-500 space-y-1">
                          {type.features.map((feature, index) => (
                            <li key={index}>• {feature}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Step 3: Geometry */}
              {currentStep === 3 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Geometria regeneratora
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Długość [m] *
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        value={configData.geometry.length}
                        onChange={(e) => setConfigData({
                          ...configData,
                          geometry: {...configData.geometry, length: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Szerokość [m] *
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        value={configData.geometry.width}
                        onChange={(e) => setConfigData({
                          ...configData,
                          geometry: {...configData.geometry, width: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Wysokość całkowita [m] *
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        value={configData.geometry.height}
                        onChange={(e) => setConfigData({
                          ...configData,
                          geometry: {...configData.geometry, height: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Wysokość checkera [m] *
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0.1"
                        value={configData.geometry.checker_height}
                        onChange={(e) => setConfigData({
                          ...configData,
                          geometry: {...configData.geometry, checker_height: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Obliczone wartości:</h4>
                    <div className="text-sm text-blue-700 grid grid-cols-2 gap-4">
                      <div>Objętość: {(configData.geometry.length * configData.geometry.width * configData.geometry.height).toFixed(2)} m³</div>
                      <div>Powierzchnia podstawy: {(configData.geometry.length * configData.geometry.width).toFixed(2)} m²</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Materials */}
              {currentStep === 4 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Wybór materiałów
                  </h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Materiał checkera *
                      </label>
                      <select
                        value={configData.materials.checker_material_id}
                        onChange={(e) => setConfigData({
                          ...configData,
                          materials: {...configData.materials, checker_material_id: e.target.value}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Wybierz materiał checkera</option>
                        {materials.filter(m => m.material_type === 'refractory' || m.material_type === 'checker').map((material) => (
                          <option key={material.id} value={material.id}>
                            {material.name} - {material.manufacturer || 'Unknown'}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Materiał ścian *
                      </label>
                      <select
                        value={configData.materials.wall_material_id}
                        onChange={(e) => setConfigData({
                          ...configData,
                          materials: {...configData.materials, wall_material_id: e.target.value}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Wybierz materiał ścian</option>
                        {materials.filter(m => m.material_type === 'insulation' || m.material_type === 'refractory').map((material) => (
                          <option key={material.id} value={material.id}>
                            {material.name} - {material.manufacturer || 'Unknown'}
                          </option>
                        ))}
                      </select>
                    </div>
                    {materials.length === 0 && (
                      <div className="text-center py-8">
                        <p className="text-gray-500 mb-4">Brak dostępnych materiałów w bibliotece.</p>
                        <button
                          onClick={loadMaterials}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                          Odśwież listę materiałów
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Step 5: Operating Conditions */}
              {currentStep === 5 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Warunki pracy
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Przepływ powietrza [m³/h] *
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={configData.operating_conditions.air_flow_rate}
                        onChange={(e) => setConfigData({
                          ...configData,
                          operating_conditions: {
                            ...configData.operating_conditions,
                            air_flow_rate: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Przepływ gazu [m³/h] *
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={configData.operating_conditions.gas_flow_rate}
                        onChange={(e) => setConfigData({
                          ...configData,
                          operating_conditions: {
                            ...configData.operating_conditions,
                            gas_flow_rate: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Temperatura wlotu powietrza [°C] *
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={configData.operating_conditions.air_inlet_temp}
                        onChange={(e) => setConfigData({
                          ...configData,
                          operating_conditions: {
                            ...configData.operating_conditions,
                            air_inlet_temp: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Temperatura wlotu gazu [°C] *
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={configData.operating_conditions.gas_inlet_temp}
                        onChange={(e) => setConfigData({
                          ...configData,
                          operating_conditions: {
                            ...configData.operating_conditions,
                            gas_inlet_temp: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ciśnienie projektowe [Pa] *
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={configData.operating_conditions.design_pressure}
                        onChange={(e) => setConfigData({
                          ...configData,
                          operating_conditions: {
                            ...configData.operating_conditions,
                            design_pressure: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 6: Thermal Properties */}
              {currentStep === 6 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Właściwości termiczne
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Docelowa sprawność [%] *
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={configData.thermal_properties.target_efficiency}
                        onChange={(e) => setConfigData({
                          ...configData,
                          thermal_properties: {
                            ...configData.thermal_properties,
                            target_efficiency: parseFloat(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Maksymalna temperatura pracy [°C] *
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={configData.thermal_properties.max_operating_temp}
                        onChange={(e) => setConfigData({
                          ...configData,
                          thermal_properties: {
                            ...configData.thermal_properties,
                            max_operating_temp: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Limit spadku ciśnienia [Pa] *
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={configData.thermal_properties.pressure_drop_limit}
                        onChange={(e) => setConfigData({
                          ...configData,
                          thermal_properties: {
                            ...configData.thermal_properties,
                            pressure_drop_limit: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 7: Summary */}
              {currentStep === 7 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">
                    Podsumowanie konfiguracji
                  </h2>
                  <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-2">Podstawowe informacje</h3>
                      <p><strong>Nazwa:</strong> {configData.name}</p>
                      <p><strong>Typ:</strong> {configData.regenerator_type}</p>
                      {configData.description && <p><strong>Opis:</strong> {configData.description}</p>}
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-2">Geometria</h3>
                      <p><strong>Wymiary:</strong> {configData.geometry.length} × {configData.geometry.width} × {configData.geometry.height} m</p>
                      <p><strong>Wysokość checkera:</strong> {configData.geometry.checker_height} m</p>
                      <p><strong>Objętość:</strong> {(configData.geometry.length * configData.geometry.width * configData.geometry.height).toFixed(2)} m³</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-2">Warunki pracy</h3>
                      <p><strong>Przepływ powietrza:</strong> {configData.operating_conditions.air_flow_rate.toLocaleString()} m³/h</p>
                      <p><strong>Przepływ gazu:</strong> {configData.operating_conditions.gas_flow_rate.toLocaleString()} m³/h</p>
                      <p><strong>Temperatura wlotu:</strong> {configData.operating_conditions.air_inlet_temp}°C / {configData.operating_conditions.gas_inlet_temp}°C</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-2">Właściwości termiczne</h3>
                      <p><strong>Docelowa sprawność:</strong> {configData.thermal_properties.target_efficiency}%</p>
                      <p><strong>Maksymalna temperatura:</strong> {configData.thermal_properties.max_operating_temp}°C</p>
                      <p><strong>Limit spadku ciśnienia:</strong> {configData.thermal_properties.pressure_drop_limit.toLocaleString()} Pa</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation */}
              <div className="flex justify-between mt-8 pt-6 border-t">
                <button
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className={`px-6 py-2 rounded-md ${
                    currentStep === 1
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gray-600 text-white hover:bg-gray-700'
                  }`}
                >
                  ← Wstecz
                </button>

                {currentStep < 7 ? (
                  <button
                    onClick={nextStep}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Dalej →
                  </button>
                ) : (
                  <button
                    onClick={saveConfiguration}
                    disabled={isLoading}
                    className={`px-6 py-2 rounded-md ${
                      isLoading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700'
                    } text-white`}
                  >
                    {isLoading ? 'Zapisywanie...' : 'Zapisz konfigurację'}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* 3D Visualization Panel (Placeholder) */}
          <div className="w-96">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Wizualizacja 3D
              </h3>
              <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Wizualizacja 3D regeneratora
                  </p>
                  <p className="text-gray-500 text-xs mt-2">
                    Będzie zaimplementowana w następnej iteracji
                  </p>
                </div>
              </div>

              {/* Current Configuration Summary */}
              <div className="mt-6 text-sm">
                <h4 className="font-medium text-gray-900 mb-2">Aktualnie:</h4>
                <div className="space-y-1 text-gray-600">
                  <div>Typ: {configData.regenerator_type}</div>
                  <div>Wymiary: {configData.geometry.length}×{configData.geometry.width}×{configData.geometry.height}m</div>
                  <div>Sprawność: {configData.thermal_properties.target_efficiency}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default withAuth(ConfiguratorPage);