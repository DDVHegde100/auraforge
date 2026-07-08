import Editor from "./pages/Editor";
import Research from "./pages/Research";
import Showcase from "./pages/Showcase";

function route() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  if (path === "/showcase") return <Showcase />;
  if (path === "/research") return <Research />;
  return <Editor />;
}

export default function App() {
  return route();
}
