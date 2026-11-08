// ESLint checks the JavaScript inside <script> tags of our HTML pages (and any .js files).
// Goal: catch real bugs (undefined names, typos, duplicate keys), not style.
import js from "@eslint/js";
import html from "eslint-plugin-html";
import globals from "globals";

export default [
  { ignores: ["node_modules/**", "**/*.min.js"] },
  js.configs.recommended,
  {
    files: ["**/*.html", "**/*.js"],
    plugins: { html },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: { ...globals.browser, d3: "readonly" }
    },
    rules: {
      "no-unused-vars": ["warn", { args: "none" }],
      "no-empty": ["error", { allowEmptyCatch: true }]
    }
  },
  {
    files: ["eslint.config.js"],
    languageOptions: { sourceType: "module", globals: globals.node }
  }
];
