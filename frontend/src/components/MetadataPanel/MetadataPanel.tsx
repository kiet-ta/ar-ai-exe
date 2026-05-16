import type { ModelAsset, ScanSession } from "../../types";

type MetadataPanelProps = {
  scanSession: ScanSession | null;
  modelAsset: ModelAsset | null;
};

export function MetadataPanel({ scanSession, modelAsset }: MetadataPanelProps) {
  return (
    <aside className="metadata-panel">
      <section className="panel-section">
        <h2>Scan</h2>
        {scanSession ? (
          <dl>
            <dt>Session</dt>
            <dd>{scanSession.id}</dd>
            <dt>Status</dt>
            <dd>{scanSession.status}</dd>
            <dt>Model</dt>
            <dd>{scanSession.modelAssetId ?? "pending"}</dd>
          </dl>
        ) : (
          <p className="muted">No scan loaded.</p>
        )}
      </section>

      <section className="panel-section">
        <h2>Quality</h2>
        {modelAsset ? (
          <dl>
            {Object.entries(modelAsset.qualityReport).map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{String(value)}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="muted">Quality report appears after processing completes.</p>
        )}
      </section>
    </aside>
  );
}
