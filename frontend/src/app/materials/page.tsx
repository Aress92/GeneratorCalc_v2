'use client'

import { useState, useEffect } from 'react'
import { MaterialsAPI } from '@/lib/api-client'
import { withAuth } from '@/contexts/AuthContext'
// TODO: Re-enable sonner after fixing pnpm installation
// import { toast } from 'sonner'

// Temporary toast fallback until sonner is installed
const toast = {
  success: (msg: string) => console.log('✅', msg),
  error: (msg: string) => console.error('❌', msg),
  warning: (msg: string) => console.warn('⚠️', msg),
  info: (msg: string) => console.info('ℹ️', msg),
};

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
// import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  Database,
  Thermometer,
  Weight,
  Layers,
  RefreshCw,
  Download,
  Upload
} from 'lucide-react'

interface Material {
  id: string
  name: string
  description: string
  material_type: string
  category: string
  properties: {
    density: number
    thermal_conductivity: number
    specific_heat: number
    max_temperature: number
  }
  chemical_composition: Record<string, number>
  is_active: boolean
  is_standard: boolean
}

function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [newMaterial, setNewMaterial] = useState({
    name: '',
    description: '',
    material_type: 'refractory',
    category: 'alumina',
    application: 'high_temp',
    properties: {
      thermal_conductivity: 0,
      specific_heat: 0,
      density: 0,
      max_temperature: 0
    }
  })

  const materialTypes = [
    'refractory', 'insulation', 'checker', 'structural', 'sealing', 'other'
  ]

  useEffect(() => {
    loadMaterials()
  }, [])

  const loadMaterials = async () => {
    try {
      setLoading(true)

      // Load materials in two batches to get all 105 materials
      const [batch1, batch2] = await Promise.all([
        MaterialsAPI.getMaterials({
          limit: 100,
          offset: 0
        }),
        MaterialsAPI.getMaterials({
          limit: 100,
          offset: 100
        })
      ])

      const materialsData1 = Array.isArray(batch1) ? batch1 : (batch1 as any)?.materials || []
      const materialsData2 = Array.isArray(batch2) ? batch2 : (batch2 as any)?.materials || []

      setMaterials([...materialsData1, ...materialsData2])
    } catch (error) {
      console.error('Failed to load materials:', error)
    } finally {
      setLoading(false)
    }
  }

  const createMaterial = async () => {
    try {
      await MaterialsAPI.createMaterial(newMaterial)
      setShowCreateDialog(false)
      setNewMaterial({
        name: '',
        description: '',
        material_type: 'refractory',
        category: 'alumina',
        application: 'high_temp',
        properties: {
          thermal_conductivity: 0,
          specific_heat: 0,
          density: 0,
          max_temperature: 0
        }
      })
      await loadMaterials()
      toast.success('Materiał został utworzony pomyślnie')
    } catch (error) {
      console.error('Failed to create material:', error)
      toast.error(`Nie udało się utworzyć materiału: ${error instanceof Error ? error.message : 'Nieznany błąd'}`)
    }
  }

  const exportMaterials = () => {
    const csvContent = "data:text/csv;charset=utf-8," + [
      'Name,Type,Category,Thermal Conductivity,Specific Heat,Density,Max Temperature',
      ...materials.map(m => `${m.name},${m.material_type},${m.category},${m.properties.thermal_conductivity},${m.properties.specific_heat},${m.properties.density},${m.properties.max_temperature}`)
    ].join('\n')

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', 'materials.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const filteredMaterials = materials.filter(material => {
    const matchesSearch = material.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         material.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = !selectedType || material.material_type === selectedType
    const matchesCategory = !selectedCategory || material.category === selectedCategory

    return matchesSearch && matchesType && matchesCategory
  })

  const getMaterialTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      refractory: 'bg-red-100 text-red-800',
      insulation: 'bg-blue-100 text-blue-800',
      checker: 'bg-green-100 text-green-800',
      metal: 'bg-gray-100 text-gray-800',
      cement: 'bg-yellow-100 text-yellow-800',
      coating: 'bg-purple-100 text-purple-800',
      default: 'bg-gray-100 text-gray-800'
    }
    return colors[type] || colors.default
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Ładowanie bazy materiałów...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Database className="h-8 w-8 text-blue-600" />
                <div>
                  <CardTitle className="text-3xl font-bold text-gray-900">
                    Baza materiałów
                  </CardTitle>
                  <p className="text-gray-600 mt-1">
                    Zarządzaj katalogiem materiałów ogniotrwałych i izolacyjnych
                  </p>
                </div>
              </div>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                Dodaj materiał
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* Filters and Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <Label htmlFor="search">Szukaj materiału</Label>
                <div className="relative mt-1">
                  <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
                  <Input
                    id="search"
                    placeholder="Nazwa lub opis..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="type">Typ materiału</Label>
                <select
                  id="type"
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Wszystkie typy</option>
                  {materialTypes.map(type => (
                    <option key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="category">Kategoria</Label>
                <select
                  id="category"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Wszystkie kategorie</option>
                  <option value="alumina">Alumina</option>
                  <option value="silica">Silica</option>
                  <option value="ceramic_fiber">Ceramic Fiber</option>
                  <option value="chrome">Chrome</option>
                  <option value="cordierite">Cordierite</option>
                </select>
              </div>

              <div className="flex items-end gap-2">
                <Button
                  variant="outline"
                  onClick={loadMaterials}
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Odśwież
                </Button>
                <Button
                  onClick={() => setShowCreateDialog(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Dodaj
                </Button>
                <Button
                  variant="outline"
                  onClick={exportMaterials}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Database className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Łącznie materiałów</p>
                  <p className="text-2xl font-bold text-gray-900">{materials.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Layers className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Standardowe</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {materials.filter(m => m.is_standard).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Thermometer className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Ogniotrwałe</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {materials.filter(m => m.material_type === 'refractory').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center">
                <Weight className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Izolacyjne</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {materials.filter(m => m.material_type === 'insulation').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Materials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMaterials.map((material) => (
            <Card key={material.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold text-gray-900 mb-2">
                      {material.name}
                    </CardTitle>
                    <div className="flex gap-2 mb-2">
                      <Badge className={getMaterialTypeColor(material.material_type)}>
                        {material.material_type}
                      </Badge>
                      {material.is_standard && (
                        <Badge variant="outline">Standard</Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-1">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  {material.description}
                </p>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Gęstość:</span>
                    <span className="font-medium">{material.properties.density} kg/m³</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Przewodność cieplna:</span>
                    <span className="font-medium">{material.properties.thermal_conductivity} W/mK</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Ciepło właściwe:</span>
                    <span className="font-medium">{material.properties.specific_heat} J/kgK</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Max temperatura:</span>
                    <span className="font-medium">{material.properties.max_temperature}°C</span>
                  </div>
                </div>

                {material.chemical_composition && Object.keys(material.chemical_composition).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Skład chemiczny:</p>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(material.chemical_composition).slice(0, 3).map(([element, percentage]) => (
                        <Badge key={element} variant="secondary" className="text-xs">
                          {element}: {percentage}%
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredMaterials.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Brak materiałów
                </h3>
                <p className="text-gray-600 mb-4">
                  Nie znaleziono materiałów spełniających kryteria wyszukiwania.
                </p>
                <Button onClick={() => {
                  setSearchTerm('')
                  setSelectedType('')
                  setSelectedCategory('')
                }}>
                  Wyczyść filtry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Create Material Form */}
        {showCreateDialog && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Dodaj nowy materiał</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Nazwa</Label>
                  <Input
                    id="name"
                    value={newMaterial.name}
                    onChange={(e) => setNewMaterial({...newMaterial, name: e.target.value})}
                    placeholder="Nazwa materiału"
                  />
                </div>

                <div>
                  <Label htmlFor="description">Opis</Label>
                  <Input
                    id="description"
                    value={newMaterial.description}
                    onChange={(e) => setNewMaterial({...newMaterial, description: e.target.value})}
                    placeholder="Opis materiału"
                  />
                </div>

                <div>
                  <Label htmlFor="type">Typ materiału</Label>
                  <select
                    id="type"
                    value={newMaterial.material_type}
                    onChange={(e) => setNewMaterial({...newMaterial, material_type: e.target.value})}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                  >
                    {materialTypes.map(type => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="thermal_conductivity">Przewodność cieplna (W/mK)</Label>
                    <Input
                      id="thermal_conductivity"
                      type="number"
                      step="0.1"
                      value={newMaterial.properties.thermal_conductivity}
                      onChange={(e) => setNewMaterial({
                        ...newMaterial,
                        properties: {...newMaterial.properties, thermal_conductivity: parseFloat(e.target.value) || 0}
                      })}
                    />
                  </div>

                  <div>
                    <Label htmlFor="specific_heat">Ciepło właściwe (J/kgK)</Label>
                    <Input
                      id="specific_heat"
                      type="number"
                      step="1"
                      value={newMaterial.properties.specific_heat}
                      onChange={(e) => setNewMaterial({
                        ...newMaterial,
                        properties: {...newMaterial.properties, specific_heat: parseFloat(e.target.value) || 0}
                      })}
                    />
                  </div>

                  <div>
                    <Label htmlFor="density">Gęstość (kg/m³)</Label>
                    <Input
                      id="density"
                      type="number"
                      step="1"
                      value={newMaterial.properties.density}
                      onChange={(e) => setNewMaterial({
                        ...newMaterial,
                        properties: {...newMaterial.properties, density: parseFloat(e.target.value) || 0}
                      })}
                    />
                  </div>

                  <div>
                    <Label htmlFor="max_temperature">Max temperatura (°C)</Label>
                    <Input
                      id="max_temperature"
                      type="number"
                      step="1"
                      value={newMaterial.properties.max_temperature}
                      onChange={(e) => setNewMaterial({
                        ...newMaterial,
                        properties: {...newMaterial.properties, max_temperature: parseFloat(e.target.value) || 0}
                      })}
                    />
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateDialog(false)}
                    className="flex-1"
                  >
                    Anuluj
                  </Button>
                  <Button
                    onClick={createMaterial}
                    className="flex-1"
                    disabled={!newMaterial.name || !newMaterial.description}
                  >
                    Dodaj materiał
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default withAuth(MaterialsPage)