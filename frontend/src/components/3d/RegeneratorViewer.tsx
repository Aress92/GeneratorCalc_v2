'use client'

import React, { Suspense, useRef, useState, useEffect, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, Grid, Box, Text, Html } from '@react-three/drei'
import * as THREE from 'three'

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

interface RegeneratorViewerProps {
  config: RegeneratorConfig
  showTemperatureMap?: boolean
  showFlow?: boolean
  className?: string
}

// Regenerator main structure component
function RegeneratorStructure({ config }: { config: RegeneratorConfig }) {
  const meshRef = useRef<THREE.Group>(null)

  const { length, width, height, wall_thickness } = config.geometry

  return (
    <group ref={meshRef}>
      {/* Main chamber walls */}
      <group>
        {/* Front wall */}
        <Box
          position={[0, height/2, length/2 + wall_thickness/2]}
          args={[width + 2*wall_thickness, height, wall_thickness]}
        >
          <meshStandardMaterial color="#8B4513" />
        </Box>

        {/* Back wall */}
        <Box
          position={[0, height/2, -length/2 - wall_thickness/2]}
          args={[width + 2*wall_thickness, height, wall_thickness]}
        >
          <meshStandardMaterial color="#8B4513" />
        </Box>

        {/* Left wall */}
        <Box
          position={[-width/2 - wall_thickness/2, height/2, 0]}
          args={[wall_thickness, height, length]}
        >
          <meshStandardMaterial color="#8B4513" />
        </Box>

        {/* Right wall */}
        <Box
          position={[width/2 + wall_thickness/2, height/2, 0]}
          args={[wall_thickness, height, length]}
        >
          <meshStandardMaterial color="#8B4513" />
        </Box>

        {/* Bottom floor */}
        <Box
          position={[0, wall_thickness/2, 0]}
          args={[width, wall_thickness, length]}
        >
          <meshStandardMaterial color="#654321" />
        </Box>
      </group>

      {/* Checker bricks pattern */}
      <CheckerPattern config={config} />

      {/* Gas inlet/outlet ports */}
      <GasPorts config={config} />
    </group>
  )
}

// Checker brick pattern component
function CheckerPattern({ config }: { config: RegeneratorConfig }) {
  const { length, width, height } = config.geometry
  const { height: checkerHeight, spacing, pattern } = config.checker

  const checkers = []
  const checkerSpacing = checkerHeight + spacing
  const numCheckersX = Math.floor(width / checkerSpacing)
  const numCheckersZ = Math.floor(length / checkerSpacing)

  for (let i = 0; i < numCheckersX; i++) {
    for (let j = 0; j < numCheckersZ; j++) {
      const x = (i - numCheckersX/2 + 0.5) * checkerSpacing
      const z = (j - numCheckersZ/2 + 0.5) * checkerSpacing
      const y = checkerHeight/2 + config.geometry.wall_thickness

      checkers.push(
        <CheckerBrick
          key={`checker-${i}-${j}`}
          position={[x, y, z]}
          size={[checkerHeight * 0.8, checkerHeight, checkerHeight * 0.8]}
          pattern={pattern}
        />
      )
    }
  }

  return <group>{checkers}</group>
}

// Individual checker brick component
function CheckerBrick({
  position,
  size,
  pattern
}: {
  position: [number, number, number]
  size: [number, number, number]
  pattern: string
}) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      // Subtle breathing animation for thermal visualization
      const scale = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.02
      meshRef.current.scale.setScalar(scale)
    }
  })

  const getPatternGeometry = () => {
    switch (pattern) {
      case 'honeycomb':
        return <cylinderGeometry args={[size[0]/2, size[0]/2, size[1], 6]} />
      case 'crossflow':
        return (
          <group>
            <boxGeometry args={size} />
            {/* Cross-flow channels */}
            <Box position={[0, 0, size[2]/4]} args={[size[0]*0.3, size[1]*1.1, size[2]*0.3]}>
              <meshBasicMaterial transparent opacity={0} />
            </Box>
          </group>
        )
      default: // brick
        return <boxGeometry args={size} />
    }
  }

  return (
    <mesh ref={meshRef} position={position}>
      {getPatternGeometry()}
      <meshStandardMaterial
        color="#CD853F"
        roughness={0.8}
        metalness={0.1}
      />
    </mesh>
  )
}

// Gas ports component
function GasPorts({ config }: { config: RegeneratorConfig }) {
  const { length, width, height } = config.geometry
  const portRadius = Math.min(width, length) * 0.1

  return (
    <group>
      {/* Inlet port */}
      <mesh position={[0, height + 0.5, length/3]}>
        <cylinderGeometry args={[portRadius, portRadius, 1, 8]} />
        <meshStandardMaterial color="#FF6B35" emissive="#FF2000" emissiveIntensity={0.3} />
      </mesh>

      {/* Outlet port */}
      <mesh position={[0, height + 0.5, -length/3]}>
        <cylinderGeometry args={[portRadius, portRadius, 1, 8]} />
        <meshStandardMaterial color="#4A90E2" emissive="#0066CC" emissiveIntensity={0.2} />
      </mesh>

      {/* Port labels */}
      <Html position={[0, height + 1.2, length/3]}>
        <div className="text-white text-sm font-bold bg-red-600 px-2 py-1 rounded">
          Inlet {config.thermal?.gas_temp_inlet || 1600}°C
        </div>
      </Html>

      <Html position={[0, height + 1.2, -length/3]}>
        <div className="text-white text-sm font-bold bg-blue-600 px-2 py-1 rounded">
          Outlet {config.thermal?.gas_temp_outlet || 600}°C
        </div>
      </Html>
    </group>
  )
}

// Temperature visualization overlay
function TemperatureMap({ config, show }: { config: RegeneratorConfig, show: boolean }) {
  if (!show) return null

  const { length, width, height } = config.geometry
  const tempInlet = config.thermal?.gas_temp_inlet || 1600
  const tempOutlet = config.thermal?.gas_temp_outlet || 600

  // Create temperature gradient zones
  const zones = []
  const numZones = 5

  for (let i = 0; i < numZones; i++) {
    const z = (i - numZones/2 + 0.5) * (length / numZones)
    const tempRatio = i / (numZones - 1)
    const temperature = tempInlet - (tempInlet - tempOutlet) * tempRatio

    // Color based on temperature (red = hot, blue = cold)
    const tempNormalized = (temperature - tempOutlet) / (tempInlet - tempOutlet)
    const red = Math.floor(255 * tempNormalized)
    const blue = Math.floor(255 * (1 - tempNormalized))
    const color = `rgb(${red}, 100, ${blue})`

    zones.push(
      <mesh key={`temp-zone-${i}`} position={[0, height/2, z]}>
        <boxGeometry args={[width*0.8, height*0.8, length/numZones*0.8]} />
        <meshBasicMaterial
          transparent
          opacity={0.3}
          color={color}
        />
      </mesh>
    )
  }

  return (
    <group>
      {zones}
      {/* Temperature scale indicator */}
      <Html position={[width/2 + 1, height, 0]}>
        <div className="bg-black/70 text-white p-2 rounded text-xs">
          <div className="font-bold mb-1">Temperature Scale</div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>{tempInlet}°C</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>{tempOutlet}°C</span>
          </div>
        </div>
      </Html>
    </group>
  )
}

// Loading component
function Loader() {
  return (
    <Html center>
      <div className="text-white text-lg">Loading 3D Model...</div>
    </Html>
  )
}

// Flow visualization component
function FlowVisualization({ config, show }: { config: RegeneratorConfig, show: boolean }) {
  const { length, width, height } = config.geometry
  const arrowsRef = useRef<THREE.Group>(null)

  const arrows = useMemo(() => {
    if (!show) return []

    const arrowElements = []
    for (let i = 0; i < 5; i++) {
      arrowElements.push(
        <mesh key={`flow-arrow-${i}`} position={[0, height/2, (i - 2) * (length / 4)]}>
          <coneGeometry args={[0.2, 0.6, 8]} />
          <meshBasicMaterial color="#00FF00" transparent opacity={0.7} />
        </mesh>
      )
    }
    return arrowElements
  }, [show, length, height])

  useFrame((state) => {
    if (!show || !arrowsRef.current) return

    arrowsRef.current.children.forEach((arrow, index) => {
      const offset = Math.sin(state.clock.elapsedTime * 2 + index * 0.5) * 0.1
      arrow.position.z = (index - 2) * (length / 4) + offset
    })
  })

  if (!show) return null

  return (
    <group ref={arrowsRef}>
      {arrows}
    </group>
  )
}

// Temperature visualization component
function TemperatureVisualization({ config, show }: { config: RegeneratorConfig, show: boolean }) {
  if (!show) return null

  const { length, width, height } = config.geometry
  const tempData = config.thermal || { gas_temp_inlet: 1600, gas_temp_outlet: 600 }

  return (
    <group>
      {/* Temperature gradient visualization */}
      <Html position={[width/2 + 1, height, 0]}>
        <div className="bg-black/70 text-white p-2 rounded text-xs">
          <div className="font-bold mb-1">Temperature Profile</div>
          <div>Inlet: {tempData.gas_temp_inlet || 1600}°C</div>
          <div>Outlet: {tempData.gas_temp_outlet || 600}°C</div>
        </div>
      </Html>

      {/* Visual temperature gradient */}
      <mesh position={[0, height + 0.5, 0]}>
        <boxGeometry args={[length, 0.1, width]} />
        <meshBasicMaterial color="#FF4500" transparent opacity={0.5} />
      </mesh>
    </group>
  )
}

// Loading fallback component
function LoadingFallback() {
  return (
    <Html center>
      <div className="bg-black/70 text-white p-4 rounded-lg">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
        <div>Loading 3D Model...</div>
      </div>
    </Html>
  )
}

// Main component export
export default function RegeneratorViewer({
  config,
  showTemperatureMap = false,
  showFlow = false
}: RegeneratorViewerProps) {
  return (
    <div className="w-full h-96 bg-gray-100 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [15, 10, 15], fov: 60 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, 10, -10]} intensity={0.5} />

        <Suspense fallback={<LoadingFallback />}>
          <RegeneratorStructure config={config} />
          <CheckerPattern config={config} />

          {showFlow && <FlowVisualization config={config} show={showFlow} />}
          {showTemperatureMap && <TemperatureVisualization config={config} show={showTemperatureMap} />}

          <OrbitControls enablePan enableZoom enableRotate />
        </Suspense>
      </Canvas>
    </div>
  )
}