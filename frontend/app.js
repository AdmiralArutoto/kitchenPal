const recipeGrid = document.getElementById("recipeGrid");
const recipeForm = document.getElementById("recipeForm");
const refreshBtn = document.getElementById("refreshRecipes");
const cancelEditBtn = document.getElementById("cancelEdit");
const formStatus = document.getElementById("formStatus");
const formTitle = document.getElementById("formTitle");
const chatBtn = document.getElementById("chatSubmit");
const chatPrompt = document.getElementById("chatPrompt");
const chatStatus = document.getElementById("chatStatus");
const chatReply = document.getElementById("chatReply");
const chatSuggestions = document.getElementById("chatSuggestions");
const openaiKeyInput = document.getElementById("openaiKey");

let editingId = null;
let chatHistory = [];

const api = {
  async request(path, options = {}) {
    const headers = {"Content-Type": "application/json", ...(options.headers || {})};
    const response = await fetch(path, {...options, headers});
    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Request failed");
    }
    if (response.status === 204) {
      return null;
    }
    return response.json();
  },
  listRecipes() {
    return this.request("/recipes/");
  },
  createRecipe(payload) {
    return this.request("/recipes/", {method: "POST", body: JSON.stringify(payload)});
  },
  updateRecipe(id, payload) {
    return this.request(`/recipes/${id}`, {method: "PUT", body: JSON.stringify(payload)});
  },
  deleteRecipe(id) {
    return this.request(`/recipes/${id}`, {method: "DELETE"});
  },
  saveChatRecipe(recipe) {
    return this.request("/chat/recipes", {method: "POST", body: JSON.stringify({recipe})});
  },
  async chat(messages, apiKey) {
    return this.request("/chat/respond", {
      method: "POST",
      headers: {"X-OpenAI-Key": apiKey},
      body: JSON.stringify({messages}),
    });
  },
};

function parseList(value) {
  return value
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function parseTags(value) {
  return value
    .split(/[,\n]+/)
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function populateForm(recipe) {
  document.getElementById("title").value = recipe.title || "";
  document.getElementById("description").value = recipe.description || "";
  document.getElementById("ingredients").value = (recipe.ingredients || []).join("\n");
  document.getElementById("steps").value = (recipe.steps || []).join("\n");
  document.getElementById("tags").value = (recipe.tags || []).join(", ");
}

function resetForm() {
  recipeForm.reset();
  editingId = null;
  formTitle.textContent = "Create Recipe";
  cancelEditBtn.classList.add("hidden");
  formStatus.textContent = "";
}

function handleEdit(recipe) {
  editingId = recipe.id;
  populateForm(recipe);
  formTitle.textContent = "Edit Recipe";
  cancelEditBtn.classList.remove("hidden");
  document.getElementById("title").focus();
}

function createCard(recipe) {
  const template = document.getElementById("recipeCardTemplate");
  const card = template.content.firstElementChild.cloneNode(true);
  card.querySelector(".card-title").textContent = recipe.title;
  card.querySelector(".card-description").textContent = recipe.description || "";

  const ingredients = card.querySelector(".ingredients");
  recipe.ingredients.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    ingredients.appendChild(li);
  });

  const steps = card.querySelector(".steps");
  recipe.steps.forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    steps.appendChild(li);
  });

  const tags = card.querySelector(".tags");
  recipe.tags.forEach((tag) => {
    const span = document.createElement("span");
    span.textContent = tag;
    tags.appendChild(span);
  });

  card.querySelector(".edit").addEventListener("click", () => handleEdit(recipe));
  card.querySelector(".delete").addEventListener("click", async () => {
    if (!confirm(`Delete ${recipe.title}?`)) return;
    await api.deleteRecipe(recipe.id);
    await loadRecipes();
  });

  return card;
}

async function loadRecipes() {
  recipeGrid.innerHTML = "";
  try {
    const recipes = await api.listRecipes();
    if (!recipes.length) {
      recipeGrid.innerHTML = "<p>No recipes yet. Start by creating one.</p>";
      return;
    }
    const fragment = document.createDocumentFragment();
    recipes.forEach((recipe) => {
      fragment.appendChild(createCard(recipe));
    });
    recipeGrid.appendChild(fragment);
  } catch (error) {
    recipeGrid.innerHTML = `<p class="status">Failed to load recipes: ${error.message}</p>`;
  }
}

recipeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: document.getElementById("title").value.trim(),
    description: document.getElementById("description").value.trim() || null,
    ingredients: parseList(document.getElementById("ingredients").value),
    steps: parseList(document.getElementById("steps").value),
    tags: parseTags(document.getElementById("tags").value),
  };

  formStatus.textContent = "Saving...";
  try {
    if (editingId) {
      await api.updateRecipe(editingId, payload);
    } else {
      await api.createRecipe(payload);
    }
    formStatus.textContent = "Saved!";
    resetForm();
    await loadRecipes();
  } catch (error) {
    formStatus.textContent = error.message;
  }
});

cancelEditBtn.addEventListener("click", resetForm);
refreshBtn.addEventListener("click", loadRecipes);

function renderSuggestions(suggestions) {
  chatSuggestions.innerHTML = "";
  if (!suggestions.length) return;
  suggestions.forEach((recipe) => {
    const card = document.createElement("div");
    card.className = "suggestion-card";
    card.innerHTML = `
      <h4>${recipe.title}</h4>
      <p>${recipe.description || ""}</p>
      <small>${recipe.ingredients.length} ingredients, ${recipe.steps.length} steps</small>
      <button class="primary">Save to Catalog</button>
    `;
    card.querySelector("button").addEventListener("click", async () => {
      try {
        await api.saveChatRecipe(recipe);
        await loadRecipes();
        card.querySelector("button").textContent = "Saved";
        card.querySelector("button").disabled = true;
      } catch (error) {
        alert(`Failed to save recipe: ${error.message}`);
      }
    });
    chatSuggestions.appendChild(card);
  });
}

async function askKitchenPal() {
  const apiKey = openaiKeyInput.value.trim();
  const prompt = chatPrompt.value.trim();
  if (!apiKey) {
    chatStatus.textContent = "Enter your OpenAI API key.";
    return;
  }
  if (!prompt) {
    chatStatus.textContent = "Ask a question first.";
    return;
  }

  chatStatus.textContent = "Asking KitchenPal...";
  chatReply.textContent = "";
  chatSuggestions.innerHTML = "";
  chatBtn.disabled = true;

  chatHistory.push({role: "user", content: prompt});
  try {
    const response = await api.chat(chatHistory, apiKey);
    chatHistory.push({role: "assistant", content: response.reply});
    chatReply.textContent = response.reply;
    renderSuggestions(response.suggestions);
    chatStatus.textContent = "";
  } catch (error) {
    chatStatus.textContent = error.message;
  } finally {
    chatBtn.disabled = false;
  }
}

chatBtn.addEventListener("click", askKitchenPal);

loadRecipes();
