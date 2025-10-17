'use client'

import React, { Suspense, useRef, useState, useEffect } from 'react'
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
  if (!show) return null

  const { length, width, height } = config.geometry
  const arrowsRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (arrowsRef.current) {
      arrowsRef.current.children.forEach((arrow, index) => {
        const offset = Math.sin(state.clock.elapsedTime * 2 + index * 0.5) * 0.1
        arrow.position.z = (index - 2) * (length / 4) + offset
      })
    }
  })

  const arrows = []
  for (let i = 0; i < 5; i++) {
    arrows.push(
      <mesh key={`flow-arrow-${i}`} position={[0, height/2, (i - 2) * (length / 4)]}>
        <coneGeometry args={[0.2, 0.6, 8]} />
        <meshBasicMaterial color="#00FF00" transparent opacity={0.7} />
      </mesh>
    )
  }

  return (
    <group ref={arrowsRef}>
      {arrows}
      {/* Flow direction indicator */}
      <Html position={[-width/2 - 1, height, 0]}>
        <div className="bg-black/70 text-white p-2 rounded text-xs">
          <div className="font-bold mb-1">Gas Flow</div>
          <div className="flex items-center gap-1">
            <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-b-[8px] border-b-green-500"></div>
            <span>Direction</span>
          </div>
        </div>
      </Html>
    </group>
  )
}

// Main RegeneratorViewer component
export default function RegeneratorViewer({
  config,
  showTemperatureMap = false,
  showFlow = false,
  className = ""
}: RegeneratorViewerProps) {
  const [isWireframe, setIsWireframe] = useState(false)
  const [localShowTemperature, setLocalShowTemperature] = useState(showTemperatureMap)
  const [localShowFlow, setLocalShowFlow] = useState(showFlow)

  // Update local state when props change
  useEffect(() => {
    setLocalShowTemperature(showTemperatureMap)
  }, [showTemperatureMap])

  useEffect(() => {
    setLocalShowFlow(showFlow)
  }, [showFlow])

  return (
    <div className={`relative w-full h-full ${className}`}>
      <Canvas
        camera={{
          position: [10, 8, 10],
          fov: 60,
          near: 0.1,
          far: 1000
        }}
        shadows
      >
        <Suspense fallback={<Loader />}>
          {/* Lighting */}
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[10, 10, 10]}
            intensity={1}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[0, 10, 0]} intensity={0.5} color="#FFA500" />

          {/* Environment and controls */}
          <Environment preset="warehouse" />
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={5}
            maxDistance={50}
          />

          {/* Ground grid */}
          <Grid
            position={[0, -1, 0]}
            args={[20, 20]}
            cellSize={1}
            cellThickness={0.5}
            cellColor="#666666"
            sectionSize={5}
            sectionThickness={1}
            sectionColor="#888888"
          />

          {/* Main regenerator structure */}
          <RegeneratorStructure config={config} />

          {/* Temperature overlay */}
          <TemperatureMap config={config} show={localShowTemperature} />

          {/* Flow visualization */}
          <FlowVisualization config={config} show={localShowFlow} />

        </Suspense>
      </Canvas>

      {/* Controls overlay */}
      <div className="absolute top-4 right-4 bg-black/50 p-3 rounded-lg text-white space-y-2">
        <h3 className="font-bold">3D Controls</h3>
        <div className="text-sm space-y-1">
          <div>• Mouse: Rotate view</div>
          <div>• Scroll: Zoom in/out</div>
          <div>• Right-click: Pan</div>
        </div>
        <div className="space-y-2 pt-2 border-t border-white/20">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={localShowTemperature}
              onChange={(e) => setLocalShowTemperature(e.target.checked)}
            />
            <span>Temperature Map</span>
          </label>
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={localShowFlow}
              onChange={(e) => setLocalShowFlow(e.target.checked)}
            />
            <span>Flow Visualization</span>
          </label>
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={isWireframe}
              onChange={() => setIsWireframe(!isWireframe)}
            />
            <span>Wireframe</span>
          </label>
        </div>
      </div>

      {/* Info panel */}
      <div className="absolute bottom-4 left-4 bg-black/50 p-3 rounded-lg text-white">
        <h4 className="font-bold mb-2">Regenerator Specs</h4>
        <div className="text-sm space-y-1">
          <div>Dimensions: {config.geometry.length}×{config.geometry.width}×{config.geometry.height}m</div>
          <div>Wall: {config.geometry.wall_thickness}m thick</div>
          <div>Checker: {config.checker.height}m, {config.checker.spacing}m spacing</div>
          <div>Pattern: {config.checker.pattern}</div>
        </div>
      </div>
    </div>
  )
}