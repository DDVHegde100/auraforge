import { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("checking api…");
  const [lookCount, setLookCount] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/health").then((r) => r.json()),
      fetch("/api/looks").then((r) => r.json()),
    ])
      .then(([health, looks]) => {
        setStatus(health.ok ? `engine ${health.engine}` : "api down");
        setLookCount(looks.count ?? 0);
      })
      .catch(() => setStatus("api offline — run ./dev.sh"));
  }, []);

  return (
    <main className="shell">
      <h1>auraforge</h1>
      <p className="tag">my version of luminar neo but free</p>
      <p className="muted">{status}</p>
      {lookCount !== null && (
        <p className="muted">{lookCount} looks registered (stubs for now)</p>
      )}
      <p className="muted">local files only. more enhance / grades / signatures land in later commits.</p>
    </main>
  );
}
