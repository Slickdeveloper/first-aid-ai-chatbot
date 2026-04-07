type EmergencyBannerProps = {
  emergency: boolean;
  recommendedAction?: string;
};

export function EmergencyBanner({
  emergency,
  recommendedAction,
}: EmergencyBannerProps) {
  if (!emergency) {
    return null;
  }

  return (
    <aside>
      {/* The warning is visually separated so urgent guidance is hard to miss. */}
      <strong>Emergency warning</strong>
      <p>{recommendedAction ?? "Call local emergency services immediately."}</p>
    </aside>
  );
}
