type ErrorBannerProps = {
  message: string;
  offline?: boolean;
  onRetry?: () => void;
};

export function ErrorBanner({ message, offline, onRetry }: ErrorBannerProps) {
  return (
    <div className={`error-banner ${offline ? "offline" : ""}`} role="alert">
      <p>{message}</p>
      {onRetry && (
        <button type="button" className="tool-btn" onClick={onRetry}>
          retry
        </button>
      )}
    </div>
  );
}
