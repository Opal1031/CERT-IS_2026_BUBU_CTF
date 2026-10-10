(() => {
  const defaultSort = "popularity DESC, id ASC";
  const sortSelect = document.getElementById("sort-select");
  const status = document.getElementById("booth-status");
  const list = document.getElementById("booth-list");
  let activeRequest;

  function createTextElement(tag, className, value) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = String(value ?? "");
    return element;
  }

  function renderBooths(booths) {
    const cards = document.createDocumentFragment();

    for (const booth of booths) {
      const card = document.createElement("article");
      card.className = "booth";

      const top = createTextElement("div", "booth-top", "");
      top.append(
        createTextElement("span", "booth-id", `BOOTH ${String(booth.id ?? "").padStart(2, "0")}`),
        createTextElement("span", "booth-category", booth.category)
      );

      const footer = createTextElement("div", "booth-footer", "");
      footer.append(
        createTextElement("span", "", `위치 · ${booth.location ?? ""}`),
        createTextElement("span", "", `관심도 · ${booth.popularity ?? ""}`)
      );

      card.append(
        top,
        createTextElement("h3", "", booth.name),
        createTextElement("p", "", booth.description),
        footer
      );
      cards.append(card);
    }

    list.replaceChildren(cards);
  }

  async function loadBooths(sort) {
    activeRequest?.abort();
    activeRequest = new AbortController();
    status.classList.remove("error");
    status.textContent = "부스 정보를 불러오는 중입니다.";

    try {
      const response = await fetch(`/api/booths?sort=${encodeURIComponent(sort)}`, {
        signal: activeRequest.signal,
        headers: { Accept: "application/json" }
      });
      if (!response.ok) throw new Error("request failed");

      const result = await response.json();
      if (!Array.isArray(result.booths)) throw new Error("invalid response");

      renderBooths(result.booths);
      status.textContent = result.booths.length
        ? `총 ${result.booths.length}개 부스를 표시합니다.`
        : "표시할 부스가 없습니다.";
    } catch (error) {
      if (error.name === "AbortError") return;
      list.replaceChildren();
      status.classList.add("error");
      status.textContent = "부스 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
    }
  }

  function selectSort(sort) {
    const known = [...sortSelect.options].some((option) => option.value === sort);
    if (!known) {
      const custom = document.createElement("option");
      custom.value = sort;
      custom.textContent = "공유된 정렬 기준";
      custom.dataset.custom = "true";
      sortSelect.append(custom);
    }
    sortSelect.value = sort;
  }

  function currentSort() {
    const params = new URLSearchParams(window.location.search);
    return params.has("sort") ? params.get("sort") : defaultSort;
  }

  function setSort(sort) {
    const url = new URL(window.location.href);
    url.searchParams.set("sort", sort);
    window.history.replaceState(null, "", url);
    selectSort(sort);
    loadBooths(sort);
  }

  sortSelect.addEventListener("change", () => {
    sortSelect.querySelector("[data-custom]")?.remove();
    setSort(sortSelect.value);
  });
  window.addEventListener("popstate", () => {
    const sort = currentSort();
    selectSort(sort);
    loadBooths(sort);
  });

  const initialSort = currentSort();
  selectSort(initialSort);
  loadBooths(initialSort);
})();
