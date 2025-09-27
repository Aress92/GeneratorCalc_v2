'use client'

import React, { useMemo } from 'react'
import RegeneratorViewer from '@/components/3d/RegeneratorViewer'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Eye, Download, AlertTriangle, CheckCircle } from 'lucide-react'

interface ImportedRegenerator {
  id?: string
  name: string
  regenerator_type: 'crown' | 'endport' | 'crossfired'
  geometry_config: {
    length: number
    width: number
    height: number
    wall_thickness: number
  }
  checker_config: {
    height: number
    spacing: number
    pattern: 'honeycomb' | 'brick' | 'crossflow'
  }
  materials_config: {
    wall_material: string
    checker_material: string
    insulation_material: string
  }
  thermal_config: {
    gas_temp_inlet: number
    gas_temp_outlet: number
  }
  // Validation status
  validation_status?: 'valid' | 'warning' | 'error'
  validation_messages?: string[]
}

interface ImportPreview3DProps {
  regenerators: ImportedRegenerator[]
  selectedIndex: number
  onSelectRegenator: (index: number) => void
  onValidateAll: () => void
  onDownloadTemplate: () => void
  className?: string
}

export default function ImportPreview3D({
  regenerators,
  selectedIndex,
  onSelectRegenator,
  onValidateAll,
  onDownloadTemplate,
  className = ""
}: ImportPreview3DProps) {
  const currentRegenator = regenerators[selectedIndex]

  // Convert imported regenerator to 3D viewer format
  const regeneratorConfig = useMemo(() => {
    if (!currentRegenator) return null

    return {
      geometry: {
        length: currentRegenator.geometry_config.length,
        width: currentRegenator.geometry_config.width,
        height: currentRegenator.geometry_config.height,
        wall_thickness: currentRegenator.geometry_config.wall_thickness
      },
      checker: {
        height: currentRegenator.checker_config.height,
        spacing: currentRegenator.checker_config.spacing,
        pattern: currentRegenator.checker_config.pattern
      },
      materials: {
        wall_material: currentRegenator.materials_config.wall_material,
        checker_material: currentRegenator.materials_config.checker_material,
        insulation_material: currentRegenator.materials_config.insulation_material
      },
      thermal: {
        gas_temp_inlet: currentRegenator.thermal_config.gas_temp_inlet,
        gas_temp_outlet: currentRegenator.thermal_config.gas_temp_outlet
      }
    }
  }, [currentRegenator])

  const getValidationBadge = (status?: string) => {
    switch (status) {
      case 'valid':
        return <Badge variant="secondary" className="bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Valid</Badge>
      case 'warning':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800"><AlertTriangle className="h-3 w-3 mr-1" />Warning</Badge>
      case 'error':
        return <Badge variant="destructive"><AlertTriangle className="h-3 w-3 mr-1" />Error</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  if (!currentRegenator || !regeneratorConfig) {
    return (
      <div className={`w-full ${className}`}>
        <Card>
          <CardContent className="flex items-center justify-center h-96">
            <div className="text-center space-y-4">
              <Eye className="h-16 w-16 mx-auto text-muted-foreground" />
              <div>
                <h3 className="text-lg font-semibold">No Regenerator Selected</h3>
                <p className="text-muted-foreground">Import a file to see 3D preview</p>
              </div>
              <Button onClick={onDownloadTemplate} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download Template
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className={`w-full space-y-4 ${className}`}>
      {/* Header with regenerator selector */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              3D Preview: {currentRegenator.name}
              {getValidationBadge(currentRegenator.validation_status)}
            </CardTitle>
            <div className="flex items-center gap-2">
              <select
                value={selectedIndex}
                onChange={(e) => onSelectRegenator(Number(e.target.value))}
                className="px-3 py-1 border rounded-md text-sm"
              >
                {regenerators.map((regen, index) => (
                  <option key={index} value={index}>
                    {regen.name} ({regen.regenerator_type})
                  </option>
                ))}
              </select>
              <Badge variant="outline">
                {selectedIndex + 1} of {regenerators.length}
              </Badge>
              <Button onClick={onValidateAll} variant="outline" size="sm">
                Validate All
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Regenerator specifications */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Specifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h4 className="font-semibold text-sm">Type</h4>
                <p className="text-sm text-muted-foreground capitalize">{currentRegenator.regenerator_type}</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Dimensions (L×W×H)</h4>
                <p className="text-sm text-muted-foreground">
                  {regeneratorConfig.geometry.length} × {regeneratorConfig.geometry.width} × {regeneratorConfig.geometry.height} m
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Wall Thickness</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.geometry.wall_thickness} m</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Checker Pattern</h4>
                <p className="text-sm text-muted-foreground capitalize">
                  {regeneratorConfig.checker.pattern} ({regeneratorConfig.checker.height}m)
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Materials</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h4 className="font-semibold text-sm">Wall Material</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.materials.wall_material}</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Checker Material</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.materials.checker_material}</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Insulation</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.materials.insulation_material}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Thermal</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <h4 className="font-semibold text-sm">Inlet Temperature</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.thermal.gas_temp_inlet}°C</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Outlet Temperature</h4>
                <p className="text-sm text-muted-foreground">{regeneratorConfig.thermal.gas_temp_outlet}°C</p>
              </div>

              <div>
                <h4 className="font-semibold text-sm">Temperature Drop</h4>
                <p className="text-sm text-muted-foreground">
                  {regeneratorConfig.thermal.gas_temp_inlet - regeneratorConfig.thermal.gas_temp_outlet}°C
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Validation messages */}
          {currentRegenator.validation_messages && currentRegenator.validation_messages.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  Validation Issues
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {currentRegenator.validation_messages.map((message, index) => (
                    <div key={index} className="text-sm p-2 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800">
                      {message}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 3D Viewer */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Interactive 3D Model
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="h-[600px] w-full">
                <RegeneratorViewer
                  config={regeneratorConfig}
                  showTemperatureMap={true}
                  showFlow={false}
                  className="h-full rounded-lg"
                />
              </div>
            </CardContent>
          </Card>

          {/* Navigation controls */}
          <div className="flex justify-between items-center mt-4">
            <Button
              onClick={() => onSelectRegenator(Math.max(0, selectedIndex - 1))}
              disabled={selectedIndex === 0}
              variant="outline"
            >
              ← Previous
            </Button>

            <div className="flex gap-2">
              {regenerators.map((_, index) => (
                <button
                  key={index}
                  onClick={() => onSelectRegenator(index)}
                  className={`w-3 h-3 rounded-full ${
                    index === selectedIndex
                      ? 'bg-primary'
                      : 'bg-muted hover:bg-muted-foreground/20'
                  }`}
                />
              ))}
            </div>

            <Button
              onClick={() => onSelectRegenator(Math.min(regenerators.length - 1, selectedIndex + 1))}
              disabled={selectedIndex === regenerators.length - 1}
              variant="outline"
            >
              Next →
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}