type IconProps = { size?: number; className?: string };

export function IconEnhance({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path
        fill="currentColor"
        d="M12 2l1.4 4.3L18 8l-4.6 1.7L12 14l-1.4-4.3L6 8l4.6-1.7L12 2zm-7 9l1 3.1L9 15l-3.1 1.1L5 19l-1-3.1L1 15l3.1-1.1L5 11zm14 0l1 3.1L23 15l-3.1 1.1L19 19l-1-3.1L15 15l3.1-1.1L19 11zM12 16l.8 2.5 2.5.9-2.5.9L12 23l-.8-2.5-2.5-.9 2.5-.9L12 16z"
      />
    </svg>
  );
}

export function IconPalette({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path
        fill="currentColor"
        d="M12 3a9 9 0 100 18h1.5a2.5 2.5 0 000-5H12a1 1 0 01-1-1v-.5A6.5 6.5 0 0112 3zm-4 7a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm8 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm-4-4a1.5 1.5 0 110-3 1.5 1.5 0 010 3z"
      />
    </svg>
  );
}

export function IconCamera({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path
        fill="currentColor"
        d="M9 4l1.2-2h3.6L15 4h4a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2h4zm3 14a5 5 0 100-10 5 5 0 000 10z"
      />
    </svg>
  );
}

export function IconFx({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 3l6-3-6-3v6z" />
    </svg>
  );
}

export function IconSliders({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path
        fill="currentColor"
        d="M4 8h9v2H4V8zm11 0h5v2h-5V8zM4 14h5v2H4v-2zm7 0h9v2h-9v-2zM10 5h2v6h-2V5zm2 8h2v6h-2v-6z"
      />
    </svg>
  );
}

export function IconExport({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M12 3v10.6l3.3-3.3 1.4 1.4L12 17.4 7.3 12.7l1.4-1.4L12 13.6V3zm-7 14h14v2H5v-2z" />
    </svg>
  );
}

export function IconUndo({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M12.5 8c-2.65 0-5.05 1-6.9 2.6L2 7v9h9l-3.4-3.4A7.96 7.96 0 0112.5 10c3.04 0 5.78 1.46 7.48 3.74L22 12.5A9.96 9.96 0 0012.5 8z" />
    </svg>
  );
}

export function IconFolder({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M10 4l2 2h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2h6z" />
    </svg>
  );
}

export function IconCompare({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M3 5h8v14H3V5zm10 0h8v14h-8V5zM9 7H5v10h4V7zm10 0h-4v10h4V7z" />
    </svg>
  );
}

export function IconUpload({ size = 18, className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden>
      <path fill="currentColor" d="M11 16V7.8l-2.6 2.6L7 9l5-5 5 5-1.4 1.4L13 7.8V16h-2zm-6 2h14v2H5v-2z" />
    </svg>
  );
}
