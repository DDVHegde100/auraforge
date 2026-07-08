import Editor from "./pages/Editor";
import Showcase from "./pages/Showcase";

function route() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  if (path === "/showcase") return <Showcase />;
  return <Editor />;
}

export default function App() {
  return route();
}
