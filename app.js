let scene, camera, renderer, terrainMesh, sensorRing;

function init() {
  const container = document.getElementById('canvas-container');
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 6, 8);
  camera.lookAt(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  container.appendChild(renderer.domElement);

  // Holographic Wireframe Grid (Terrain Simulation)
  const gridGeo = new THREE.PlaneGeometry(12, 12, 24, 24);
  const gridMat = new THREE.MeshBasicMaterial({ color: 0x00ff88, wireframe: true, transparent: true, opacity: 0.4 });
  terrainMesh = new THREE.Mesh(gridGeo, gridMat);
  terrainMesh.rotation.x = -Math.PI / 2;
  scene.add(terrainMesh);

  // Quantum Sensor Indicator
  const ringGeo = new THREE.RingGeometry(0.8, 0.85, 32);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0xffb700, side: THREE.DoubleSide });
  sensorRing = new THREE.Mesh(ringGeo, ringMat);
  sensorRing.rotation.x = -Math.PI / 2;
  sensorRing.position.y = 0.1;
  scene.add(sensorRing);

  window.addEventListener('resize', onResize);
  animate();
}

function animate() {
  requestAnimationFrame(animate);
  sensorRing.rotation.z += 0.02;
  renderer.render(scene, camera);
}

function scanAnomalies() {
  const log = document.getElementById('term-log');
  log.innerHTML += `<br>[SCAN] Magnetic Anomaly detected at ΔB = +410 nT. Subsurface target locked.`;
  sensorRing.scale.set(1.5, 1.5, 1.5);
  setTimeout(() => sensorRing.scale.set(1, 1, 1), 400);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

window.onload = init;
