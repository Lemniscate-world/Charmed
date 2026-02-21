# Walkthrough: Ollama API Key Support

I have updated the Ollama provider in Void to support API keys. This allows you to use Ollama not just locally, but also with cloud-hosted or remote Ollama instances that require authentication.

## Changes Made

### Configuration & UI
- **[modelCapabilities.ts](file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/common/modelCapabilities.ts)**: Added `apiKey` to the default settings for the Ollama provider.
- **[voidSettingsTypes.ts](file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/common/voidSettingsTypes.ts)**: Updated the settings UI metadata so that the "API Key" field is rendered when Ollama is selected.

### LLM Message Pipeline
- **[sendLLMMessage.impl.ts](file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/electron-main/llmMessage/sendLLMMessage.impl.ts)**:
    - Updated `newOpenAICompatibleSDK` to use the provided API key for Ollama chat requests.
    - Updated `newOllamaSDK` to include the API key in the `Authorization` header for model listing and FIM (Fill-In-Middle) requests.
    - Ensured that local usage (empty API key) still works as expected.


## Detailed Explanations

### 1. What is `product.json`?
Think of **[product.json](file:///home/kuro/Documents/Astral/product.json)** as the identity card of the application. It tells the operating system and the user's computer:
- **`nameShort` & `nameLong`**: The name displayed in menus and titles (currently "Void").
- **`applicationName`**: The name of the actual executable file (currently "void").
- **`dataFolderName`**: Where your settings and extensions are stored (e.g., `~/.void-editor`).
- **`extensionsGallery`**: Where the editor looks for plugins.

### 2. What is Gulp?
**Gulp** is like a "factory manager" for your code. When you write code, it's just a bunch of text files. Gulp automates the process of:
1. Turning that text into something a computer can run (compiling).
2. Bundling files together.
3. Creating the final installer (like the `.deb` file).
You talk to Gulp using the `gulp` command, followed by a specific "task" name (like `vscode-linux-x64-build-deb`).

### 3. What is a Hashmap?
A **Hashmap** (often called an `Object` or `Map` in JavaScript/TypeScript) is like a real-world dictionary.
- In a dictionary, you look up a **Word** (the Key) to find its **Definition** (the Value).
- In a Hashmap, you provide a unique key (like "ollama") to instantly get a value (like the Ollama settings).
- **Rule of Thumb**: We use the naming convention `bOfA` for maps. For example, `settingsOfProvider` is a map where you give it a `provider` and get back its `settings`.

## Building a `.deb` for testing
I've checked your system, and you have both `dpkg-deb` and `fakeroot` installed, which are the tools needed to build the installer.

**To try a test build:**
1.  **Install dependencies**: Run `npm install` (this takes a while and uses a lot of space).
2.  **Compile the code**: Run `npm run compile`.
3.  **Run the build command**:
    ```bash
    gulp vscode-linux-x64-build-deb
    ```
    The resulting file will appear in `.build/linux/deb/`.

## AI Rules Integration
I've expanded **[.voidrules](file:///home/kuro/Documents/Astral/.voidrules)** to include **all** your guidelines from `kuro-rules`. I've categorized them into principles like **SRP** (Single Responsibility), **Security**, and **Agent Protocols**.
> [!IMPORTANT]
> I have confirmed that these rules are applied to **our coding process** on this repository, ensuring that every change I make follows your high standards for security, quality, and clarity.

render_diffs(file:///home/kuro/Documents/Astral/.voidrules)
render_diffs(file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/common/modelCapabilities.ts)
render_diffs(file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/common/voidSettingsTypes.ts)
render_diffs(file:///home/kuro/Documents/Astral/src/vs/workbench/contrib/void/electron-main/llmMessage/sendLLMMessage.impl.ts)

