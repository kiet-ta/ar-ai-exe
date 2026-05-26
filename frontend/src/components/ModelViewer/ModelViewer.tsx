import { Grid, OrbitControls, Text as DreiText, TransformControls, useGLTF, useTexture } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Fragment, Suspense, useEffect, useMemo, useRef, useState } from "react";
import type { RefObject } from "react";
import * as THREE from "three";

import type { DesignConfig, StickerLayer, TextLayer } from "../../types";
import { ErrorBoundary } from "../Layout/ErrorBoundary";

type ModelViewerProps = {
  modelUrl: string | null;
  config: DesignConfig | null;
  activeLayerId: string | null;
  onConfigChange: (config: DesignConfig) => void;
  onActiveLayerChange: (id: string | null) => void;
  onMeshBoundsUpdate: (bounds: { center: [number, number, number]; size: [number, number, number] }) => void;
  gizmoMode: "translate" | "rotate" | "scale";
};

type ModelRaycastTarget = {
  name: string;
  mesh: THREE.Mesh;
};

type LayerTransform = {
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
};

export function ModelViewer({ modelUrl, config, activeLayerId, gizmoMode, onConfigChange, onActiveLayerChange, onMeshBoundsUpdate }: ModelViewerProps) {
  return (
    <div className="viewer-surface">
      {modelUrl ? (
        <Canvas camera={{ position: [3, 2, 3], fov: 45 }} shadows>
          <color attach="background" args={["#f8fafc"]} />
          <ambientLight intensity={0.8} />
          <directionalLight position={[3, 4, 5]} intensity={1.3} castShadow />
          <ErrorBoundary fallbackMessage="Failed to load 3D model. The file might be invalid or corrupted.">
            <Suspense fallback={null}>
              <ShoeModel
                url={modelUrl}
                config={config}
                activeLayerId={activeLayerId}
                gizmoMode={gizmoMode}
                onConfigChange={onConfigChange}
                onActiveLayerChange={onActiveLayerChange}
                onMeshBoundsUpdate={onMeshBoundsUpdate}
              />
            </Suspense>
          </ErrorBoundary>
          <Grid
            args={[5, 5]}
            cellSize={0.5}
            cellThickness={0.5}
            sectionSize={1}
            sectionThickness={0.8}
            position={[0, -0.02, 0]}
          />
          <OrbitControls makeDefault enablePan enableZoom enableRotate />
        </Canvas>
      ) : (
        <div className="viewer-empty">
          <BoxIcon />
          <span>Load a completed scan or imported model.</span>
        </div>
      )}
    </div>
  );
}

type ShoeModelProps = {
  url: string;
  config: DesignConfig | null;
  activeLayerId: string | null;
  onConfigChange: (config: DesignConfig) => void;
  onActiveLayerChange: (id: string | null) => void;
  onMeshBoundsUpdate: (bounds: { center: [number, number, number]; size: [number, number, number] }) => void;
  gizmoMode: "translate" | "rotate" | "scale";
};

function ShoeModel({ url, config, activeLayerId, gizmoMode, onConfigChange, onActiveLayerChange, onMeshBoundsUpdate }: ShoeModelProps) {
  const gltf = useGLTF(url);
  const stageRef = useRef<THREE.Group>(null);

  const modelMetrics = useMemo(() => {
    const bounds = computeSceneLocalBounds(gltf.scene);
    const center = bounds.getCenter(new THREE.Vector3());
    const size = bounds.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const previewScale = maxDim > 0 ? 2.5 / maxDim : 1;
    return { center, size, previewScale };
  }, [gltf.scene]);

  const centeredModelPosition = useMemo(
    () => modelMetrics.center.clone().multiplyScalar(-1),
    [modelMetrics],
  );

  const raycastTargets = useMemo(() => createModelRaycastTargets(gltf.scene), [gltf.scene]);

  useEffect(() => {
    onMeshBoundsUpdate({
      center: vectorToTuple(modelMetrics.center),
      size: vectorToTuple(modelMetrics.size),
    });
  }, [modelMetrics, onMeshBoundsUpdate]);

  useEffect(() => {
    gltf.scene.traverse((node) => {
      if (node instanceof THREE.Mesh) {
        if (!node.userData.originalMaterial) {
          if (Array.isArray(node.material)) {
            node.userData.originalMaterial = node.material.map((m: THREE.Material) => m.clone());
          } else if (node.material) {
            node.userData.originalMaterial = node.material.clone();
          }
        }
        
        if (node.userData.originalMaterial) {
           const applyConfig = (mat: THREE.Material) => {
             const m = mat.clone();
             if (m instanceof THREE.MeshStandardMaterial || m instanceof THREE.MeshPhysicalMaterial) {
               m.color = new THREE.Color(config?.baseColor ?? "#ffffff");
               m.roughness = config?.material.roughness ?? 0.5;
               m.metalness = config?.material.metallic ?? 0;
             }
             return m;
           };

           if (Array.isArray(node.userData.originalMaterial)) {
             node.material = node.userData.originalMaterial.map(applyConfig);
           } else {
             node.material = applyConfig(node.userData.originalMaterial);
           }
        }

        node.castShadow = true;
        node.receiveShadow = true;
      }
    });
  }, [config?.baseColor, config?.material.metallic, config?.material.roughness, gltf.scene]);

  const handlePointerMissed = () => {
    onActiveLayerChange(null);
  };

  const handleTransformEnd = (id: string, isText: boolean, pos: [number, number, number], rot: [number, number, number], scale: number) => {
    if (!config) return;
    
    if (isText) {
      onConfigChange({
        ...config,
        texts: config.texts.map((t) => t.id === id ? { ...t, position: pos, rotation: rot, scale } : t)
      });
    } else {
      onConfigChange({
        ...config,
        stickers: config.stickers.map((s) =>
          s.id === id
            ? {
                ...s,
                position: pos,
                rotation: rot,
                scale,
                width: scale,
                height: scale,
                projectionDepth: Math.max(s.projectionDepth ?? 0, scale * 3, 0.05),
              }
            : s
        )
      });
    }
  };

  return (
    <group
      ref={stageRef}
      scale={modelMetrics.previewScale}
      onPointerMissed={handlePointerMissed}
    >
      <group position={centeredModelPosition}>
        <primitive object={gltf.scene} />
      </group>
      
      {config?.stickers.map((sticker) => (
        <StickerPlane 
          key={sticker.id} 
          sticker={sticker} 
          modelCenter={modelMetrics.center}
          raycastTargets={raycastTargets}
          isActive={sticker.id === activeLayerId}
          gizmoMode={gizmoMode}
          onTransformEnd={(pos, rot, s) => handleTransformEnd(sticker.id, false, pos, rot, s)}
        />
      ))}
      {config?.texts.map((textLayer) => (
        <TextPlane 
          key={textLayer.id} 
          layer={textLayer} 
          modelCenter={modelMetrics.center}
          isActive={textLayer.id === activeLayerId}
          gizmoMode={gizmoMode}
          onTransformEnd={(pos, rot, s) => handleTransformEnd(textLayer.id, true, pos, rot, s)}
        />
      ))}
    </group>
  );
}

function computeSceneLocalBounds(scene: THREE.Object3D): THREE.Box3 {
  scene.updateWorldMatrix(true, true);
  const sceneWorldInverse = scene.matrixWorld.clone().invert();
  const bounds = new THREE.Box3();
  const meshBounds = new THREE.Box3();

  scene.traverse((node) => {
    if (!(node instanceof THREE.Mesh) || !node.geometry.attributes.position) return;
    if (!node.geometry.boundingBox) {
      node.geometry.computeBoundingBox();
    }
    if (!node.geometry.boundingBox) return;

    node.updateWorldMatrix(true, false);
    meshBounds.copy(node.geometry.boundingBox);
    meshBounds.applyMatrix4(sceneWorldInverse.clone().multiply(node.matrixWorld));
    bounds.union(meshBounds);
  });

  if (bounds.isEmpty()) {
    bounds.setFromCenterAndSize(new THREE.Vector3(), new THREE.Vector3(1, 1, 1));
  }
  return bounds;
}

function createModelRaycastTargets(root: THREE.Object3D): ModelRaycastTarget[] {
  const targets: ModelRaycastTarget[] = [];

  root.traverse((node) => {
    if (!(node instanceof THREE.Mesh) || !node.geometry.attributes.position) return;

    const mesh = new THREE.Mesh(node.geometry);
    mesh.name = node.name || node.geometry.name || "model_mesh";
    mesh.matrixAutoUpdate = false;
    const relativeMatrix = getMatrixRelativeToRoot(node, root);
    mesh.matrix.copy(relativeMatrix);
    mesh.matrixWorld.copy(relativeMatrix);
    targets.push({
      name: mesh.name,
      mesh,
    });
  });

  return targets;
}

function getMatrixRelativeToRoot(object: THREE.Object3D, root: THREE.Object3D): THREE.Matrix4 {
  const chain: THREE.Object3D[] = [];
  let current: THREE.Object3D | null = object;

  while (current && current !== root) {
    chain.unshift(current);
    current = current.parent;
  }

  const matrix = new THREE.Matrix4();
  for (const item of chain) {
    item.updateMatrix();
    matrix.multiply(item.matrix);
  }

  return matrix;
}

function vectorToTuple(vector: THREE.Vector3): [number, number, number] {
  return [vector.x, vector.y, vector.z];
}

function StickerPlane({ 
  sticker, 
  modelCenter,
  raycastTargets,
  isActive, 
  gizmoMode, 
  onTransformEnd 
}: { 
  sticker: StickerLayer; 
  modelCenter: THREE.Vector3;
  raycastTargets: ModelRaycastTarget[];
  isActive: boolean; 
  gizmoMode: "translate" | "rotate" | "scale";
  onTransformEnd: (pos: [number, number, number], rot: [number, number, number], scale: number) => void;
}) {
  const texture = useTexture(sticker.imageUrl);
  texture.colorSpace = THREE.SRGBColorSpace;
  const anchorRef = useRef<THREE.Mesh>(null);
  const [draftTransform, setDraftTransform] = useState<LayerTransform | null>(null);

  useEffect(() => {
    setDraftTransform(null);
  }, [sticker.id, sticker.position, sticker.rotation, sticker.scale]);

  const transform = useMemo<LayerTransform>(() => {
    if (draftTransform) {
      return draftTransform;
    }
    const stagePosition = new THREE.Vector3(...sticker.position).sub(modelCenter);
    return {
      position: vectorToTuple(stagePosition),
      rotation: sticker.rotation,
      scale: sticker.scale,
    };
  }, [draftTransform, modelCenter, sticker.position, sticker.rotation, sticker.scale]);

  const projectedGeometry = useMemo(
    () => createProjectedStickerGeometry(sticker, transform, modelCenter, raycastTargets),
    [modelCenter, raycastTargets, sticker, transform],
  );

  const position = new THREE.Vector3(...transform.position);
  const rotation = new THREE.Euler(...transform.rotation);
  const scaleVec = new THREE.Vector3(transform.scale, transform.scale, transform.scale);

  const syncDraftFromAnchor = () => {
    if (!anchorRef.current) return;
    const p = anchorRef.current.position;
    const r = anchorRef.current.rotation;
    const s = anchorRef.current.scale;
    setDraftTransform({
      position: [p.x, p.y, p.z],
      rotation: [r.x, r.y, r.z],
      scale: Math.max(s.x, s.y, s.z),
    });
  };

  const projectedMesh = (
    <mesh geometry={projectedGeometry} name={`layer_preview_${sticker.id}`}>
      <meshStandardMaterial
        map={texture}
        transparent
        side={THREE.DoubleSide}
        depthWrite={false}
        polygonOffset
        polygonOffsetFactor={-4}
      />
    </mesh>
  );

  if (isActive) {
    return (
      <Fragment>
        {projectedMesh}
        <mesh
          ref={anchorRef}
          name={`layer_anchor_${sticker.id}`}
          position={position}
          rotation={rotation}
          scale={scaleVec}
          raycast={() => null}
        >
          <planeGeometry args={[1, 1]} />
          <meshBasicMaterial transparent opacity={0} colorWrite={false} depthWrite={false} />
        </mesh>
        <TransformControls
          object={anchorRef as RefObject<THREE.Object3D>}
          mode={gizmoMode}
          onObjectChange={syncDraftFromAnchor}
          onMouseUp={() => {
            if (anchorRef.current) {
              const p = anchorRef.current.position;
              const r = anchorRef.current.rotation;
              const s = anchorRef.current.scale;
              const savedPosition = p.clone().add(modelCenter);
              onTransformEnd(vectorToTuple(savedPosition), [r.x, r.y, r.z], Math.max(s.x, s.y, s.z));
            }
          }}
        />
      </Fragment>
    );
  }

  return projectedMesh;
}

function createProjectedStickerGeometry(
  sticker: StickerLayer,
  transform: LayerTransform,
  modelCenter: THREE.Vector3,
  raycastTargets: ModelRaycastTarget[],
): THREE.BufferGeometry {
  const cuts = clampInt(sticker.subdivisions ?? 32, 4, 128);
  const width = sticker.width ?? sticker.scale;
  const height = sticker.height ?? sticker.scale;
  const projectionDepth = Math.max(sticker.projectionDepth ?? 0, width * 2, height * 2, 0.05);
  const offset = sticker.offset ?? 0.004;
  const position = new THREE.Vector3(...transform.position);
  const quaternion = new THREE.Quaternion().setFromEuler(new THREE.Euler(...transform.rotation));
  const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(quaternion).normalize();
  const planeToStage = new THREE.Matrix4().compose(position, quaternion, new THREE.Vector3(1, 1, 1));
  const positions: number[] = [];
  const uvs: number[] = [];
  const indices: number[] = [];

  for (let row = 0; row <= cuts; row += 1) {
    const v = row / cuts;
    for (let col = 0; col <= cuts; col += 1) {
      const u = col / cuts;
      const localPoint = new THREE.Vector3((u - 0.5) * width, (v - 0.5) * height, 0);
      const stagePoint = localPoint.applyMatrix4(planeToStage);
      const projectedPoint = projectPointToModel(stagePoint, normal, projectionDepth, offset, modelCenter, raycastTargets);
      positions.push(projectedPoint.x, projectedPoint.y, projectedPoint.z);
      uvs.push(u, v);
    }
  }

  const rowWidth = cuts + 1;
  for (let row = 0; row < cuts; row += 1) {
    for (let col = 0; col < cuts; col += 1) {
      const a = row * rowWidth + col;
      const b = a + 1;
      const c = a + rowWidth;
      const d = c + 1;
      indices.push(a, b, d, a, d, c);
    }
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  return geometry;
}

function projectPointToModel(
  stagePoint: THREE.Vector3,
  normal: THREE.Vector3,
  projectionDepth: number,
  offset: number,
  modelCenter: THREE.Vector3,
  raycastTargets: ModelRaycastTarget[],
): THREE.Vector3 {
  if (raycastTargets.length === 0) {
    return stagePoint;
  }

  const scenePoint = stagePoint.clone().add(modelCenter);
  const raycaster = new THREE.Raycaster();
  raycaster.near = 0;
  raycaster.far = projectionDepth * 2;
  const candidates: THREE.Intersection[] = [];

  raycaster.set(scenePoint.clone().addScaledVector(normal, projectionDepth), normal.clone().multiplyScalar(-1));
  candidates.push(...raycaster.intersectObjects(raycastTargets.map((target) => target.mesh), false));

  raycaster.set(scenePoint.clone().addScaledVector(normal, -projectionDepth), normal);
  candidates.push(...raycaster.intersectObjects(raycastTargets.map((target) => target.mesh), false));

  if (candidates.length === 0) {
    return stagePoint;
  }

  let closest = candidates[0];
  let closestDistance = closest.point.distanceToSquared(scenePoint);
  for (const candidate of candidates.slice(1)) {
    const distance = candidate.point.distanceToSquared(scenePoint);
    if (distance < closestDistance) {
      closest = candidate;
      closestDistance = distance;
    }
  }

  const surfaceNormal = intersectionNormal(closest, normal.clone().multiplyScalar(-1));
  return closest.point.clone().sub(modelCenter).addScaledVector(surfaceNormal, offset);
}

function intersectionNormal(intersection: THREE.Intersection, fallback: THREE.Vector3): THREE.Vector3 {
  if (!intersection.face) {
    return fallback.normalize();
  }

  return intersection.face.normal
    .clone()
    .applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(intersection.object.matrixWorld))
    .normalize();
}

function clampInt(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, Math.round(value)));
}

function TextPlane({ 
  layer, 
  modelCenter,
  isActive, 
  gizmoMode, 
  onTransformEnd 
}: { 
  layer: TextLayer; 
  modelCenter: THREE.Vector3;
  isActive: boolean; 
  gizmoMode: "translate" | "rotate" | "scale";
  onTransformEnd: (pos: [number, number, number], rot: [number, number, number], scale: number) => void;
}) {
  const ref = useRef<THREE.Mesh>(null);
  const position = new THREE.Vector3(...layer.position).sub(modelCenter);
  const rotation = new THREE.Euler(...layer.rotation);
  const scaleVec = new THREE.Vector3(layer.scale, layer.scale, layer.scale);
  
  const mesh = (
    <DreiText 
      ref={ref}
      name={`layer_preview_${layer.id}`}
      position={position} 
      rotation={rotation}
      scale={scaleVec}
      color={layer.color}
      fontSize={1}
      anchorX="center"
      anchorY="middle"
    >
      {layer.value}
    </DreiText>
  );

  if (isActive) {
    return (
      <Fragment>
        {mesh}
        <TransformControls
        object={ref as RefObject<THREE.Object3D>}
        mode={gizmoMode}
        onMouseUp={() => {
          if (ref.current) {
            const p = ref.current.position;
            const r = ref.current.rotation;
            const s = ref.current.scale;
            const savedPosition = p.clone().add(modelCenter);
            onTransformEnd(vectorToTuple(savedPosition), [r.x, r.y, r.z], Math.max(s.x, s.y, s.z));
          }
        }}
        />
      </Fragment>
    );
  }

  return mesh;
}

function BoxIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" width="48" height="48">
      <path
        fill="currentColor"
        d="M12 2 3 6.5v11L12 22l9-4.5v-11L12 2Zm0 2.24 5.7 2.85L12 9.94 6.3 7.09 12 4.24ZM5 8.62l6 3v7.76l-6-3V8.62Zm8 10.76v-7.76l6-3v7.76l-6 3Z"
      />
    </svg>
  );
}
