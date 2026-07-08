export default function Research() {
  return (
    <main className="shell shell-wide editor-shell">
      <header className="editor-header">
        <div>
          <h1>research</h1>
          <p className="tag">why auraforge looks the way it does</p>
        </div>
        <nav className="editor-nav">
          <a href="/">editor</a>
          <a href="/showcase">showcase</a>
          <a href="/research" className="active">
            research
          </a>
        </nav>
      </header>

      <article className="research-doc">
        <section>
          <h2>neo-style enhance, made explicit</h2>
          <p>
            luminar neo sells minimum clicks → maximum perceived quality. auraforge reverse-engineers
            that as an inspectable recipe: scene analysis → develop params → optional masks → grades →
            signatures. no opaque magic slider.
          </p>
        </section>

        <section>
          <h2>what viewers reward</h2>
          <ul>
            <li>midtone contrast for punch without crushed blacks</li>
            <li>highlight roll-off for an expensive digital feel</li>
            <li>gentle shadow lift for editorial readability</li>
            <li>teal–orange separation while protecting skin tones</li>
            <li>selective vibrance in mids, not on skin</li>
            <li>clarity + soft background for depth-of-field proxy</li>
          </ul>
        </section>

        <section>
          <h2>pipeline</h2>
          <pre className="research-pre">
            {`load → analyze → recipe(mode) → develop
     → sky/skin masks → grade → signature
     → strength mix → preview / export`}
          </pre>
        </section>

        <section>
          <h2>look families</h2>
          <p>
            40 grades cover portrait, food, landscape, street, wedding, cinema. 20 signatures push
            further into distinctive territory (thermal, godray, neon noir…) with a pro-safe clamp for
            experimental looks.
          </p>
        </section>

        <section>
          <h2>evaluation checklist</h2>
          <ol>
            <li>subject readable in one second?</li>
            <li>skin on-line for portraits?</li>
            <li>no hue banding or posterization?</li>
            <li>shadows hold texture?</li>
            <li>highlight bloom doesn&apos;t milk the frame?</li>
            <li>works on phone JPEG and a6000 TIFF?</li>
          </ol>
        </section>

        <p className="muted">
          full notes: <code>RESEARCH.md</code> in the repo root.
        </p>
      </article>
    </main>
  );
}
