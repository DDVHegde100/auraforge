export type LookItem = {
  id: string;
  name: string;
  tags: string[];
  experimental?: boolean;
};

export type CameraMeta = {
  era?: string;
  format?: string;
  stock?: string;
  lens?: string;
  character?: string;
};

export type CameraItem = LookItem & {
  meta?: CameraMeta;
  notes?: string;
};

const STOCK_SWATCH: Record<string, string> = {
  portra: "#c4a882",
  ektar: "#8ab4c4",
  gold: "#d4a858",
  velvia: "#6a9a6a",
  tri_x: "#888888",
  cinestill: "#c47850",
  vision3: "#7a8a9a",
  pro400h: "#9ab8a0",
  superia: "#88a898",
  digital: "#6a7080",
  default: "#5a6070",
};

export function cameraSwatch(name: string, meta?: CameraMeta): string {
  const hay = `${name} ${meta?.stock ?? ""}`.toLowerCase();
  for (const [key, color] of Object.entries(STOCK_SWATCH)) {
    if (key !== "default" && hay.includes(key.replace("_", ""))) return color;
  }
  return STOCK_SWATCH.default;
}
