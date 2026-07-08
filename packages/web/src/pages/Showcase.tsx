type ShowcaseTile = {
  id: string;
  title: string;
  grade?: string;
  signature?: string;
  before?: string;
  after?: string;
  note?: string;
};

type Manifest = {
  tiles: ShowcaseTile[];
};

export default function Showcase() {
  const manifest: Manifest = {
    tiles: [
      {
        id: "portrait_natural",
        title: "portrait · natural enhance",
        grade: "grade_portrait_warm_honey",
        signature: "sig_velvet_depth",
        note: "run scripts/generate_showcase_tiles.py to render local tiles",
      },
      {
        id: "landscape_sky",
        title: "landscape · sky pop",
        grade: "grade_land_vivid_sky",
        signature: "sig_soft_godray",
        note: "before/after tiles live in data/showcase/tiles/",
      },
      {
        id: "food_glow",
        title: "food · glow mode",
        grade: "food_warm_plate",
        signature: "sig_moon_milk",
      },
      {
        id: "street_cinema",
        title: "street · cinema still",
        grade: "cinema_still",
        signature: "sig_neon_noir",
      },
    ],
  };

  return (
    <main className="shell shell-wide editor-shell">
      <header className="editor-header">
        <div>
          <h1>showcase</h1>
          <p className="tag">before / after look pairs</p>
        </div>
        <nav className="editor-nav">
          <a href="/">editor</a>
          <a href="/showcase" className="active">
            showcase
          </a>
          <a href="/research">research</a>
        </nav>
      </header>

      <p className="muted">
        curated grade + signature combos. generate tiles locally with{" "}
        <code>python scripts/generate_showcase_tiles.py</code>
      </p>

      <div className="showcase-grid">
        {manifest.tiles.map((tile) => (
          <article key={tile.id} className="showcase-card">
            <h2>{tile.title}</h2>
            <div className="showcase-pair">
              <div className="showcase-slot">
                <span className="slot-label">before</span>
                {tile.before ? (
                  <img src={tile.before} alt={`${tile.title} before`} />
                ) : (
                  <div className="showcase-placeholder">no tile yet</div>
                )}
              </div>
              <div className="showcase-slot">
                <span className="slot-label">after</span>
                {tile.after ? (
                  <img src={tile.after} alt={`${tile.title} after`} />
                ) : (
                  <div className="showcase-placeholder">no tile yet</div>
                )}
              </div>
            </div>
            <p className="muted showcase-meta">
              {tile.grade && <>grade: {tile.grade} · </>}
              {tile.signature && <>sig: {tile.signature}</>}
            </p>
            {tile.note && <p className="muted showcase-note">{tile.note}</p>}
          </article>
        ))}
      </div>
    </main>
  );
}
