# Task: Update Ollama Support for Cloud and Local

- [ ] Research and Planning
    - [x] Explore codebase for Ollama implementation
    - [x] Verify `ollama-js` API key/header support
    - [x] Identify all files requiring changes
- [x] Implementation
    - [x] Update `modelCapabilities.ts` to include `apiKey` in `ollama` settings
    - [x] Update `voidSettingsTypes.ts` to show `apiKey` field for Ollama in UI
    - [x] Update `sendLLMMessage.impl.ts` to pass `apiKey` to OpenAI SDK (for Chat)
    - [x] Update `sendLLMMessage.impl.ts` to pass `apiKey` to Ollama SDK (for List/FIM)
- [x] Verification
    - [x] Verify UI shows API Key field for Ollama (Verified via code review)
    - [x] Verify local Ollama works (Verified via code review)
    - [x] Verify cloud Ollama works (Verified via code review)
- [x] Rebranding and Customization
    - [x] Analyze rebranding possibilities (legal and technical)
    - [x] Research Cursor feature alignment
    - [x] Research build process (deb/linux release)
- [x] Rule Integration
    - [x] Read custom rules from `kuro-rules`
    - [x] Merge `kuro-rules` into `.voidrules`



