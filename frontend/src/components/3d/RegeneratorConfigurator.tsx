'use client'

import React, { useState, useEffect } from 'react'
import RegeneratorViewer from './RegeneratorViewer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Settings, Eye, Thermometer, Wind, Download, RefreshCw } from 'lucide-react'

interface RegeneratorConfig {
  geometry: {
    length: number
    width: number
    height: number
    wall_thickness: number
  }
  checker: {
    height: number
    spacing: number
    pattern: 'honeycomb' | 'brick' | 'crossflow'
  }
  materials: {
    wall_material: string
    checker_material: string
    insulation_material: string
  }
  thermal?: {
    gas_temp_inlet?: number
    gas_temp_outlet?: number
  }
}

interface RegeneratorConfiguratorProps {
  initialConfig?: Partial<RegeneratorConfig>
  onConfigChange?: (config: RegeneratorConfig) => void
  materials?: Array<{
    id: string
    name: string
    type: string
    thermal_conductivity: number
    max_temperature: number
  }>
  className?: string
}

const defaultConfig: RegeneratorConfig = {
  geometry: {
    length: 10,
    width: 8,
    height: 6,
    wall_thickness: 0.4
  },
  checker: {
    height: 0.7,
    spacing: 0.12,
    pattern: 'honeycomb'
  },
  materials: {
    wall_material: 'High Alumina Firebrick',
    checker_material: 'Cordierite Honeycomb',
    insulation_material: 'Ceramic Fiber Blanket'
  },
  thermal: {
    gas_temp_inlet: 1600,
    gas_temp_outlet: 600
  }
}

export default function RegeneratorConfigurator({
  initialConfig,
  onConfigChange,
  materials = [],
  className = ""
}: RegeneratorConfiguratorProps) {
  const [config, setConfig] = useState<RegeneratorConfig>({
    ...defaultConfig,
    ...initialConfig
  })

  const [viewSettings, setViewSettings] = useState({
    showTemperature: false,
    showFlow: false,
    showGrid: true,
    autoRotate: false
  })

  const [selectedPreset, setSelectedPreset] = useState<string>('custom')

  // Predefined regenerator presets
  const presets = {
    crown: {
      name: 'Crown Regenerator',
      geometry: { length: 12, width: 10, height: 8, wall_thickness: 0.5 },
      checker: { height: 0.8, spacing: 0.15, pattern: 'brick' as const }
    },
    endport: {
      name: 'End-Port Regenerator',
      geometry: { length: 8, width: 6, height: 5, wall_thickness: 0.3 },
      checker: { height: 0.6, spacing: 0.10, pattern: 'honeycomb' as const }
    },
    crossfired: {
      name: 'Cross-Fired Regenerator',
      geometry: { length: 10, width: 8, height: 6, wall_thickness: 0.4 },
      checker: { height: 0.7, spacing: 0.12, pattern: 'crossflow' as const }
    }
  }

  useEffect(() => {
    if (onConfigChange) {
      onConfigChange(config)
    }
  }, [config, onConfigChange])

  const updateConfig = <K extends keyof RegeneratorConfig>(
    section: K,
    updates: Partial<RegeneratorConfig[K]>
  ) => {
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], ...updates }
    }))
    setSelectedPreset('custom')
  }

  const loadPreset = (presetKey: string) => {
    if (presetKey === 'custom') return

    const preset = presets[presetKey as keyof typeof presets]
    if (preset) {
      setConfig(prev => ({
        ...prev,
        geometry: preset.geometry,
        checker: preset.checker
      }))
      setSelectedPreset(presetKey)
    }
  }

  const calculateVolume = () => {
    const { length, width, height, wall_thickness } = config.geometry
    const innerVolume = (length - 2*wall_thickness) * (width - 2*wall_thickness) * height
    return innerVolume.toFixed(2)
  }

  const calculateSurfaceArea = () => {
    const { length, width, height } = config.geometry
    const { height: checkerHeight, spacing } = config.checker

    const checkerSpacing = checkerHeight + spacing
    const numCheckers = Math.floor((width * length) / (checkerSpacing * checkerSpacing))
    const surfaceAreaPerChecker = 4 * checkerHeight * checkerHeight // Simplified

    return (numCheckers * surfaceAreaPerChecker).toFixed(0)
  }

  return (
    <div className={`w-full space-y-4 ${className}`}>
      {/* Header with presets */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Regenerator 3D Configurator
            </CardTitle>
            <div className="flex items-center gap-2">
              <Select value={selectedPreset} onValueChange={loadPreset}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Load preset..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="custom">Custom Configuration</SelectItem>
                  {Object.entries(presets).map(([key, preset]) => (
                    <SelectItem key={key} value={key}>
                      {preset.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-1" />
                Reset
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Configuration Panel */}
        <div className="space-y-4">
          <Tabs defaultValue="geometry" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="geometry">Geometry</TabsTrigger>
              <TabsTrigger value="materials">Materials</TabsTrigger>
              <TabsTrigger value="thermal">Thermal</TabsTrigger>
            </TabsList>

            <TabsContent value="geometry" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Chamber Dimensions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Length: {config.geometry.length}m</Label>
                    <Slider
                      value={[config.geometry.length]}
                      onValueChange={([value]) => updateConfig('geometry', { length: value || 5 })}
                      min={5}
                      max={20}
                      step={0.5}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Width: {config.geometry.width}m</Label>
                    <Slider
                      value={[config.geometry.width]}
                      onValueChange={([value]) => updateConfig('geometry', { width: value || 4 })}
                      min={4}
                      max={15}
                      step={0.5}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Height: {config.geometry.height}m</Label>
                    <Slider
                      value={[config.geometry.height]}
                      onValueChange={([value]) => updateConfig('geometry', { height: value || 3 })}
                      min={3}
                      max={12}
                      step={0.5}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Wall Thickness: {config.geometry.wall_thickness}m</Label>
                    <Slider
                      value={[config.geometry.wall_thickness]}
                      onValueChange={([value]) => updateConfig('geometry', { wall_thickness: value || 0.2 })}
                      min={0.2}
                      max={1.0}
                      step={0.05}
                      className="mt-2"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Checker Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Checker Height: {config.checker.height}m</Label>
                    <Slider
                      value={[config.checker.height]}
                      onValueChange={([value]) => updateConfig('checker', { height: value || 0.3 })}
                      min={0.3}
                      max={1.5}
                      step={0.05}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Checker Spacing: {config.checker.spacing}m</Label>
                    <Slider
                      value={[config.checker.spacing]}
                      onValueChange={([value]) => updateConfig('checker', { spacing: value || 0.05 })}
                      min={0.05}
                      max={0.30}
                      step={0.01}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Checker Pattern</Label>
                    <Select
                      value={config.checker.pattern}
                      onValueChange={(value) => updateConfig('checker', { pattern: value as any })}
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="honeycomb">Honeycomb</SelectItem>
                        <SelectItem value="brick">Brick Pattern</SelectItem>
                        <SelectItem value="crossflow">Cross-Flow</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="materials" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Material Selection</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Wall Material</Label>
                    <Select
                      value={config.materials.wall_material}
                      onValueChange={(value) => updateConfig('materials', { wall_material: value })}
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="High Alumina Firebrick">High Alumina Firebrick</SelectItem>
                        <SelectItem value="Silica Firebrick">Silica Firebrick</SelectItem>
                        <SelectItem value="Magnesia Chrome Brick">Magnesia Chrome Brick</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Checker Material</Label>
                    <Select
                      value={config.materials.checker_material}
                      onValueChange={(value) => updateConfig('materials', { checker_material: value })}
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Cordierite Honeycomb">Cordierite Honeycomb</SelectItem>
                        <SelectItem value="Mullite Checker Brick">Mullite Checker Brick</SelectItem>
                        <SelectItem value="Silicon Carbide Checker">Silicon Carbide Checker</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Insulation Material</Label>
                    <Select
                      value={config.materials.insulation_material}
                      onValueChange={(value) => updateConfig('materials', { insulation_material: value })}
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Ceramic Fiber Blanket">Ceramic Fiber Blanket</SelectItem>
                        <SelectItem value="Mineral Wool">Mineral Wool</SelectItem>
                        <SelectItem value="Perlite Insulation">Perlite Insulation</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="thermal" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Thermal Parameters</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Gas Inlet Temperature: {config.thermal?.gas_temp_inlet}°C</Label>
                    <Slider
                      value={[config.thermal?.gas_temp_inlet || 1600]}
                      onValueChange={([value]) => updateConfig('thermal', { gas_temp_inlet: value || 800 })}
                      min={800}
                      max={2000}
                      step={50}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Gas Outlet Temperature: {config.thermal?.gas_temp_outlet}°C</Label>
                    <Slider
                      value={[config.thermal?.gas_temp_outlet || 600]}
                      onValueChange={([value]) => updateConfig('thermal', { gas_temp_outlet: value || 200 })}
                      min={200}
                      max={1000}
                      step={25}
                      className="mt-2"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">View Options</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="temp-map" className="flex items-center gap-2">
                      <Thermometer className="h-4 w-4" />
                      Temperature Map
                    </Label>
                    <Switch
                      id="temp-map"
                      checked={viewSettings.showTemperature}
                      onCheckedChange={(checked) =>
                        setViewSettings(prev => ({ ...prev, showTemperature: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="flow-vis" className="flex items-center gap-2">
                      <Wind className="h-4 w-4" />
                      Flow Visualization
                    </Label>
                    <Switch
                      id="flow-vis"
                      checked={viewSettings.showFlow}
                      onCheckedChange={(checked) =>
                        setViewSettings(prev => ({ ...prev, showFlow: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label htmlFor="auto-rotate">Auto Rotate</Label>
                    <Switch
                      id="auto-rotate"
                      checked={viewSettings.autoRotate}
                      onCheckedChange={(checked) =>
                        setViewSettings(prev => ({ ...prev, autoRotate: checked }))
                      }
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Performance Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Calculated Properties</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span>Inner Volume:</span>
                <Badge variant="secondary">{calculateVolume()} m³</Badge>
              </div>
              <div className="flex justify-between">
                <span>Surface Area:</span>
                <Badge variant="secondary">{calculateSurfaceArea()} m²</Badge>
              </div>
              <div className="flex justify-between">
                <span>Temperature Drop:</span>
                <Badge variant="secondary">
                  {((config.thermal?.gas_temp_inlet || 1600) - (config.thermal?.gas_temp_outlet || 600))}°C
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 3D Viewer */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                3D Regenerator Preview
                {selectedPreset !== 'custom' && (
                  <Badge variant="outline">{presets[selectedPreset as keyof typeof presets]?.name}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="h-[600px] w-full">
                <RegeneratorViewer
                  config={config}
                  showTemperatureMap={viewSettings.showTemperature}
                  showFlow={viewSettings.showFlow}
                  className="h-full"
                />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}