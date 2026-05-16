import { RefreshCw, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { api, ApiError, designStorageKey } from "./api/client";
import { EditorPanels } from "./components/Editor/EditorPanels";
import { AppShell } from "./components/Layout/AppShell";
import { MetadataPanel } from "./components/MetadataPanel/MetadataPanel";
import { ModelViewer } from "./components/ModelViewer/ModelViewer";
import type { Design, DesignConfig, ExportPackage, ModelAsset, ScanSession, User } from "./types";

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [scanId, setScanId] = useState("");
  const [scanSession, setScanSession] = useState<ScanSession | null>(null);
  const [modelAsset, setModelAsset] = useState<ModelAsset | null>(null);
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [design, setDesign] = useState<Design | null>(null);
  const [designName, setDesignName] = useState("Untitled shoe design");
  const [config, setConfig] = useState<DesignConfig | null>(null);
  const [exportPackage, setExportPackage] = useState<ExportPackage | null>(null);
  const [statusMessage, setStatusMessage] = useState("Ready");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    api
      .demoLogin()
      .then(setUser)
      .catch((error) => setStatusMessage(messageFromError(error)));
  }, []);

  useEffect(() => {
    return () => {
      if (modelUrl) {
        URL.revokeObjectURL(modelUrl);
      }
    };
  }, [modelUrl]);

  const canLoad = useMemo(() => scanId.trim().length > 0, [scanId]);

  async function loadScan() {
    if (!canLoad) {
      return;
    }

    setStatusMessage("Loading scan");
    setModelAsset(null);
    setModelUrl(null);
    setExportPackage(null);

    try {
      const loadedScan = await api.getScanSession(scanId.trim());
      setScanSession(loadedScan);

      if (!loadedScan.modelAssetId) {
        setStatusMessage(`Scan is ${loadedScan.status}`);
        return;
      }

      const loadedModel = await api.getModelAsset(loadedScan.modelAssetId);
      setModelAsset(loadedModel);
      setModelUrl(await api.fetchModelBlobUrl(loadedModel));
      await loadSavedDesign(loadedModel.id);
      setStatusMessage("Model loaded");
    } catch (error) {
      setStatusMessage(messageFromError(error));
    }
  }

  async function loadSavedDesign(modelAssetId: string) {
    const savedDesignId = localStorage.getItem(designStorageKey(modelAssetId));
    if (!savedDesignId) {
      const defaultConfig = createDefaultConfig(modelAssetId);
      setConfig(defaultConfig);
      setDesign(null);
      setDesignName("Untitled shoe design");
      return;
    }

    try {
      const savedDesign = await api.getDesign(savedDesignId);
      setDesign(savedDesign);
      setDesignName(savedDesign.name);
      setConfig(savedDesign.designConfig);
    } catch {
      localStorage.removeItem(designStorageKey(modelAssetId));
      setConfig(createDefaultConfig(modelAssetId));
    }
  }

  async function saveDesign() {
    if (!modelAsset || !config) {
      return;
    }

    setIsSaving(true);
    setStatusMessage("Saving design");
    try {
      const savedDesign = design
        ? await api.updateDesign(design.id, designName, config)
        : await api.createDesign(modelAsset.id, designName, config);
      setDesign(savedDesign);
      setDesignName(savedDesign.name);
      setConfig(savedDesign.designConfig);
      localStorage.setItem(designStorageKey(modelAsset.id), savedDesign.id);
      setStatusMessage("Design saved");
    } catch (error) {
      setStatusMessage(messageFromError(error));
    } finally {
      setIsSaving(false);
    }
  }

  async function exportDesign() {
    if (!design) {
      await saveDesign();
    }

    const activeDesignId = design?.id ?? (modelAsset && localStorage.getItem(designStorageKey(modelAsset.id)));
    if (!activeDesignId) {
      setStatusMessage("Save the draft before exporting.");
      return;
    }

    try {
      setStatusMessage("Creating export package");
      const createdExport = await api.exportDesign(activeDesignId);
      setExportPackage(createdExport);
      setStatusMessage("Export package ready");
    } catch (error) {
      setStatusMessage(messageFromError(error));
    }
  }

  async function downloadExport() {
    if (!exportPackage) {
      return;
    }
    try {
      await api.downloadExport(exportPackage);
    } catch (error) {
      setStatusMessage(messageFromError(error));
    }
  }

  return (
    <AppShell user={user}>
      <main className="workspace">
        <section className="toolbar-band">
          <div className="scan-loader">
            <label>
              Scan session ID
              <input
                value={scanId}
                onChange={(event) => setScanId(event.target.value)}
                placeholder="scan_..."
              />
            </label>
            <button type="button" disabled={!canLoad} onClick={loadScan}>
              <Search size={16} aria-hidden="true" />
              Load
            </button>
            <button type="button" disabled={!scanSession} onClick={loadScan}>
              <RefreshCw size={16} aria-hidden="true" />
              Refresh
            </button>
          </div>
          <span className="status-line">{statusMessage}</span>
        </section>

        <section className="main-grid">
          <MetadataPanel scanSession={scanSession} modelAsset={modelAsset} />
          <ModelViewer modelUrl={modelUrl} config={config} />
          <EditorPanels
            config={config}
            designName={designName}
            isSaving={isSaving}
            exportPackage={exportPackage}
            onNameChange={setDesignName}
            onConfigChange={setConfig}
            onSave={saveDesign}
            onExport={exportDesign}
            onDownload={downloadExport}
          />
        </section>
      </main>
    </AppShell>
  );
}

function createDefaultConfig(modelAssetId: string): DesignConfig {
  return {
    modelAssetId,
    baseColor: "#ffffff",
    material: {
      roughness: 0.5,
      metallic: 0,
    },
    stickers: [],
    texts: [],
  };
}

function messageFromError(error: unknown): string {
  if (error instanceof ApiError) {
    return `${error.status}: ${error.message}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unexpected error";
}
