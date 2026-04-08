// Emergency banner.
//
// This appears above the assistant response when dangerous keywords are detected,
// making urgent action impossible to miss.
type EmergencyBannerProps = {
  emergency: boolean;
  recommendedAction?: string | null;
};

const GHANA_EMERGENCY_ACTION =
  "Call 112 in Ghana immediately. Police: 191, Fire: 192, Ambulance: 193.";

export function EmergencyBanner({
  emergency,
  recommendedAction,
}: EmergencyBannerProps) {
  if (!emergency) {
    return null;
  }

  return (
    <aside className="banner-card emergency-banner">
      {/* The warning is visually separated so urgent guidance is hard to miss. */}
      <div className="banner-header-row">
        <span className="warning-icon" aria-hidden="true">
          !
        </span>
        <p className="banner-title">Emergency warning</p>
        <span className="emergency-pill">Act now</span>
      </div>
      <p className="emergency-copy">{recommendedAction ?? GHANA_EMERGENCY_ACTION}</p>
      <div className="emergency-grid">
        <span className="emergency-contact">General: 112</span>
        <span className="emergency-contact">Police: 191</span>
        <span className="emergency-contact">Fire: 192</span>
        <span className="emergency-contact">Ambulance: 193</span>
      </div>
    </aside>
  );
}
