import { Download, ImagePlus, Save, Type } from "lucide-react";

import type { DesignConfig, ExportPackage } from "../../types";

type EditorPanelsProps = {
  config: DesignConfig | null;
  designName: string;
  isSaving: boolean;
  exportPackage: ExportPackage | null;
  onNameChange: (name: string) => void;
  onConfigChange: (config: DesignConfig) => void;
  onSave: () => void;
  onExport: () => void;
  onDownload: () => void;
};

export function EditorPanels({
  config,
  designName,
  isSaving,
  exportPackage,
  onNameChange,
  onConfigChange,
  onSave,
  onExport,
  onDownload,
}: EditorPanelsProps) {
  if (!config) {
    return (
      <aside className="editor-panel">
        <h2>Design Tools</h2>
        <p className="muted">Tools unlock after a completed scan model is loaded.</p>
      </aside>
    );
  }

  const update = (patch: Partial<DesignConfig>) => onConfigChange({ ...config, ...patch });

  return (
    <aside className="editor-panel">
      <section className="panel-section">
        <h2>Design Tools</h2>
        <label>
          Draft name
          <input value={designName} onChange={(event) => onNameChange(event.target.value)} />
        </label>
      </section>

      <section className="panel-section">
        <h3>Material</h3>
        <label>
          Base color
          <input
            type="color"
            value={config.baseColor}
            onChange={(event) => update({ baseColor: event.target.value })}
          />
        </label>
        <label>
          Roughness
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.material.roughness}
            onChange={(event) =>
              update({
                material: { ...config.material, roughness: Number(event.target.value) },
              })
            }
          />
        </label>
      </section>

      <section className="panel-section">
        <h3>Decals</h3>
        <div className="button-row">
          <button type="button" onClick={() => onConfigChange(addSticker(config))}>
            <ImagePlus size={16} aria-hidden="true" />
            Sticker
          </button>
          <button type="button" onClick={() => onConfigChange(addText(config))}>
            <Type size={16} aria-hidden="true" />
            Text
          </button>
        </div>
      </section>

      <section className="panel-section">
        <h3>Layers</h3>
        <div className="layer-list">
          {config.stickers.map((sticker) => (
            <div className="layer-row" key={sticker.id}>
              <span>{sticker.id}</span>
              <span>sticker</span>
            </div>
          ))}
          {config.texts.map((textLayer) => (
            <div className="layer-row" key={textLayer.id}>
              <span>{textLayer.value}</span>
              <span>text</span>
            </div>
          ))}
          {config.stickers.length === 0 && config.texts.length === 0 ? (
            <p className="muted">No decal layers yet.</p>
          ) : null}
        </div>
      </section>

      <section className="panel-section">
        <button className="primary-button" type="button" disabled={isSaving} onClick={onSave}>
          <Save size={16} aria-hidden="true" />
          {isSaving ? "Saving" : "Save Draft"}
        </button>
        <button type="button" onClick={onExport}>
          <Download size={16} aria-hidden="true" />
          Export Package
        </button>
        {exportPackage ? (
          <button type="button" onClick={onDownload}>
            <Download size={16} aria-hidden="true" />
            Download ZIP
          </button>
        ) : null}
      </section>
    </aside>
  );
}

function addSticker(config: DesignConfig): DesignConfig {
  const index = config.stickers.length + 1;
  return {
    ...config,
    stickers: [
      ...config.stickers,
      {
        id: `sticker_${String(index).padStart(3, "0")}`,
        type: "image",
        imageUrl: "/assets/stickers/flame.png",
        position: [0.25, 0.45, 0.35],
        rotation: [0, 0.35, 0],
        scale: 0.35,
      },
    ],
  };
}

function addText(config: DesignConfig): DesignConfig {
  const index = config.texts.length + 1;
  return {
    ...config,
    texts: [
      ...config.texts,
      {
        id: `text_${String(index).padStart(3, "0")}`,
        value: "TAK",
        font: "Arial",
        color: "#111111",
        position: [-0.1, 0.48, 0.42],
        rotation: [0, 0.35, 0],
        scale: 0.22,
      },
    ],
  };
}
