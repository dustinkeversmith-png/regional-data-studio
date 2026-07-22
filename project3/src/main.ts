import "maplibre-gl/dist/maplibre-gl.css";
import "./styles.css";
import { App } from "./app/App";

const root = document.querySelector<HTMLDivElement>("#app");

if (!root) {
  throw new Error("Missing #app root element");
}

new App(root).start();
