'use client'

import { useState } from 'react'
import RegeneratorConfigurator from '@/components/3d/RegeneratorConfigurator'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function ThreeDemoPage() {
  const [currentConfig, setCurrentConfig] = useState(null)

  const handleConfigChange = (config: any) => {
    setCurrentConfig(config)
    console.log('Configuration updated:', config)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-center">
              Forglass Regenerator 3D Visualization Demo
            </CardTitle>
            <p className="text-center text-muted-foreground">
              Interactive 3D configurator for glass furnace regenerators with real-time visualization
            </p>
          </CardHeader>
        </Card>

        {/* Main configurator */}
        <RegeneratorConfigurator
          onConfigChange={handleConfigChange}
          className="w-full"
        />

        {/* Configuration output (for debugging) */}
        {currentConfig && (
          <Card>
            <CardHeader>
              <CardTitle>Current Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-100 p-4 rounded-lg overflow-auto">
                {JSON.stringify(currentConfig, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Use</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-blue-600 font-bold">1</span>
                </div>
                <h3 className="font-semibold mb-1">Configure Geometry</h3>
                <p className="text-sm text-muted-foreground">
                  Adjust regenerator dimensions using the sliders in the Geometry tab
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-green-600 font-bold">2</span>
                </div>
                <h3 className="font-semibold mb-1">Select Materials</h3>
                <p className="text-sm text-muted-foreground">
                  Choose from our database of 100+ industrial materials
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-purple-600 font-bold">3</span>
                </div>
                <h3 className="font-semibold mb-1">View in 3D</h3>
                <p className="text-sm text-muted-foreground">
                  Interact with the real-time 3D model using mouse controls
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}