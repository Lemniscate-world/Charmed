import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { openUrl } from "@tauri-apps/plugin-opener";
import { X, Check } from "lucide-react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const [authUrl, setAuthUrl] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  const handleLogin = async () => {
    try {
      setStatusMessage("Génération de l'URL...");
      const url = await invoke<string>("spotify_login", {
        clientId,
        clientSecret,
      });
      setAuthUrl(url);
      await openUrl(url);
      setStatusMessage("Veuillez vous connecter dans le navigateur, puis copiez le code de l'URL de redirection (ex: ?code=...)");
    } catch (e) {
      console.error(e);
      setStatusMessage("Erreur lors de l'initialisation de la connexion: " + String(e));
    }
  };

  const handleCallback = async () => {
    try {
      setStatusMessage("Connexion en cours...");
      // Extract code from full URL if pasted, or just use the code
      let code = authCode;
      if (code.includes("code=")) {
        const match = code.match(/code=([^&]*)/);
        if (match) code = match[1];
      }
      
      await invoke("spotify_callback", { code });
      setStatusMessage("Connecté avec succès !");
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (e) {
      console.error(e);
      setStatusMessage("Erreur d'authentification: " + String(e));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md">
      <div className="glass-panel p-8 w-full max-w-lg relative">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 transition-colors"
        >
          <X size={20} className="text-white/60" />
        </button>

        <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
          <span className="text-[#1DB954]">Spotify</span> Configuration
        </h2>

        <div className="space-y-6">
          {!authUrl ? (
            <>
              <div className="space-y-2">
                <label className="text-sm text-white/60 uppercase tracking-wider font-semibold">Client ID</label>
                <input
                  type="text"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  placeholder="Entrez votre Client ID"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white outline-none focus:border-[#1DB954] transition-colors"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-white/60 uppercase tracking-wider font-semibold">Client Secret</label>
                <input
                  type="password"
                  value={clientSecret}
                  onChange={(e) => setClientSecret(e.target.value)}
                  placeholder="Entrez votre Client Secret"
                  className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white outline-none focus:border-[#1DB954] transition-colors"
                />
              </div>

              <div className="pt-4">
                <button
                  onClick={handleLogin}
                  disabled={!clientId || !clientSecret}
                  className="w-full py-3 rounded-full bg-[#1DB954] hover:bg-[#19a34a] disabled:opacity-50 disabled:cursor-not-allowed text-black font-bold transition-all flex items-center justify-center gap-2"
                >
                  Connecter Spotify
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-4 animate-fade-in">
              <div className="bg-[#1DB954]/10 border border-[#1DB954]/20 rounded-lg p-4 text-sm text-[#1DB954]">
                <p>1. Une page de connexion s'est ouverte.</p>
                <p>2. Connectez-vous et acceptez les permissions.</p>
                <p>3. Vous serez redirigé vers une page (peut-être blanche/erreur).</p>
                <p>4. Copiez l'URL complète de cette page ou le code et collez-le ci-dessous.</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm text-white/60 uppercase tracking-wider font-semibold">Code d'autorisation</label>
                <textarea
                  value={authCode}
                  onChange={(e) => setAuthCode(e.target.value)}
                  placeholder="Collez l'URL ou le code ici..."
                  className="w-full h-24 bg-white/5 border border-white/10 rounded-lg p-3 text-white outline-none focus:border-[#1DB954] transition-colors resize-none font-mono text-xs"
                />
              </div>

              <button
                onClick={handleCallback}
                disabled={!authCode}
                className="w-full py-3 rounded-full bg-white text-black hover:bg-white/90 font-bold transition-all flex items-center justify-center gap-2"
              >
                <Check size={20} />
                Valider la connexion
              </button>
            </div>
          )}

          {statusMessage && (
            <p className={`text-center text-sm ${statusMessage.includes("Erreur") ? "text-red-400" : "text-white/60"}`}>
              {statusMessage}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
