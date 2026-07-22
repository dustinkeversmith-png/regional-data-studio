import { YEARS } from "../app/config";
import type { AppState } from "../app/state";

export function renderTimeSlider(
  container: HTMLElement,
  state: AppState,
  onChange: (next: AppState) => void,
) {
  container.innerHTML = `
    <div class="control-group">
      <h2>Time range</h2>
      <label class="range-control">
        <span>Selected year: <span class="range-value">${state.selectedYear}</span></span>
        <input type="range" min="${YEARS[0]}" max="${YEARS[YEARS.length - 1]}" step="1" value="${state.selectedYear}" />
      </label>
    </div>
  `;

  container.querySelector<HTMLInputElement>("input")!.addEventListener("input", (event) => {
    onChange({ ...state, selectedYear: Number((event.currentTarget as HTMLInputElement).value) });
  });
}
