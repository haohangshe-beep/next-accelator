/** English track labels. Keep these aligned with backend TRACK_LABELS. */

export const TRACKS = [
  {
    code: "AI",
    label: "AI",
    summary: "Applied models, metrics, and workflows an employer can audit.",
  },
  {
    code: "NewSpace",
    label: "NewSpace",
    summary: "Payload specs, tests, and health logs for small-satellite teams.",
  },
  {
    code: "Robotics",
    label: "Robotics",
    summary: "Vision and field trials where an operator still closes the loop.",
  },
  {
    code: "LowAltitude",
    label: "Low Altitude Economy",
    summary: "Drone plans, airspace constraints, and evidence a client can file.",
  },
] as const;

export type TrackCode = (typeof TRACKS)[number]["code"];

const LABELS: Record<string, string> = Object.fromEntries(TRACKS.map((track) => [track.code, track.label]));

export function trackLabel(code: string): string {
  return LABELS[code] ?? code;
}

export const LEVELS = ["Foundation", "Intermediate", "Advanced"] as const;
export const DIFFICULTIES = ["Introductory", "Intermediate", "Advanced"] as const;

export const STATUS_LABELS: Record<string, string> = {
  joined: "Joined",
  submitted: "Pending review",
  changes_requested: "Changes requested",
  certified: "Certified",
  pending: "Pending review",
  approved: "Approved",
  open: "Open",
  closed: "Closed",
};

export function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status;
}
