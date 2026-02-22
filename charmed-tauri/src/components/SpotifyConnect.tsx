import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-shell";
import { Music, Check, ExternalLink, Loader2 } from "lucide-react";

interface SpotifyPlaylist {
  id: string;
  name: string;
  uri: string;
  image_url: string | null;
  track_count: number;
  owner: string;
}

interface SpotifyConnectProps {
  isAuthenticated: boolean;
  onAuthChange: (auth: boolean) => void;
  selectedPlaylist: SpotifyPlaylist | null;
  onPlaylistSelect: (playlist: SpotifyPlaylist | null) => void;
}

export default function SpotifyConnect({
  isAuthenticated,
  onAuthChange,
  selectedPlaylist,
  onPlaylistSelect,
}: SpotifyConnectProps) {
  const [playlists, setPlaylists] = useState<SpotifyPlaylist[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showPlaylistSelector, setShowPlaylistSelector] = useState(false);
  const [callbackCode, setCallbackCode] = useState("");
  const [showCallbackInput, setShowCallbackInput] = useState(false);

  // Charger les playlists quand authentifie
  useEffect(() => {
    if (isAuthenticated) {
      loadPlaylists();
    }
  }, [isAuthenticated]);

  const loadPlaylists = async () => {
    setIsLoading(true);
    try {
      const list = await invoke<SpotifyPlaylist[]>("get_spotify_playlists");
      setPlaylists(list);
    } catch (e) {
      console.error("Erreur chargement playlists:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      // Recupere les credentials depuis les variables d'environnement
      const clientId = import.meta.env.VITE_SPOTIFY_CLIENT_ID || "";
      const clientSecret = import.meta.env.VITE_SPOTIFY_CLIENT_SECRET || "";

      if (!clientId) {
        alert("Veuillez configurer VITE_SPOTIFY_CLIENT_ID dans le fichier .env");
        return;
      }

      const authUrl = await invoke<string>("spotify_login", {
        clientId,
        clientSecret,
      });

      // Ouvrir l'URL dans le navigateur
      await open(authUrl);
      setShowCallbackInput(true);
    } catch (e) {
      console.error("Erreur login Spotify:", e);
      alert(`Erreur: ${e}`);
    }
  };

  const handleCallback = async () => {
    if (!callbackCode.trim()) {
      alert("Veuillez entrer le code d'autorisation");
      return;
    }

    setIsLoading(true);
    try {
      // Extraire le code de l'URL si l'utilisateur a colle l'URL complete
      let code = callbackCode;
      if (callbackCode.includes("code=")) {
        const match = callbackCode.match(/code=([^&]+)/);
        if (match) {
          code = match[1];
        }
      }

      await invoke("spotify_callback", { code });
      onAuthChange(true);
      setShowCallbackInput(false);
      setCallbackCode("");
      await loadPlaylists();
    } catch (e) {
      console.error("Erreur callback:", e);
      alert(`Erreur d'authentification: ${e}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-[#1DB954] flex items-center justify-center">
            <Music size={20} className="text-black" />
          </div>
          <div>
            <h3 className="font-semibold">Spotify</h3>
            <p className="text-white/40 text-sm">Non connecte</p>
          </div>
        </div>

        {!showCallbackInput ? (
          <button
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-[#1DB954] hover:bg-[#19a34a] text-black font-semibold transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <>
                <ExternalLink size={18} />
                Connecter Spotify
              </>
            )}
          </button>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-white/60">
              Apres autorisation, copiez le code depuis l'URL de redirection:
            </p>
            <input
              type="text"
              value={callbackCode}
              onChange={(e) => setCallbackCode(e.target.value)}
              placeholder="Code ou URL complete"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 outline-none focus:border-[#1DB954]"
            />
            <div className="flex gap-2">
              <button
                onClick={() => setShowCallbackInput(false)}
                className="flex-1 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleCallback}
                disabled={isLoading}
                className="flex-1 py-2 rounded-xl bg-[#1DB954] hover:bg-[#19a34a] text-black font-semibold transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <>
                    <Check size={18} />
                    Valider
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Statut connecte */}
      <div className="glass-panel p-4 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#1DB954] flex items-center justify-center">
            <Check size={16} className="text-black" />
          </div>
          <div>
            <p className="font-medium">Spotify connecte</p>
            <p className="text-white/40 text-xs">{playlists.length} playlists</p>
          </div>
        </div>
        <button
          onClick={() => setShowPlaylistSelector(!showPlaylistSelector)}
          className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors text-sm"
        >
          {selectedPlaylist ? "Changer" : "Selectionner"}
        </button>
      </div>

      {/* Playlist selectionnee */}
      {selectedPlaylist && !showPlaylistSelector && (
        <div className="glass-panel p-4 rounded-2xl flex items-center gap-3">
          {selectedPlaylist.image_url ? (
            <img
              src={selectedPlaylist.image_url}
              alt={selectedPlaylist.name}
              className="w-12 h-12 rounded-lg object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center">
              <Music size={20} className="text-white/40" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{selectedPlaylist.name}</p>
            <p className="text-white/40 text-xs">
              {selectedPlaylist.track_count} pistes - {selectedPlaylist.owner}
            </p>
          </div>
        </div>
      )}

      {/* Selector de playlists */}
      {showPlaylistSelector && (
        <div className="glass-panel p-4 rounded-2xl max-h-80 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium">Selectionner une playlist</h4>
            <button
              onClick={() => setShowPlaylistSelector(false)}
              className="text-white/40 hover:text-white"
            >
              Fermer
            </button>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 size={24} className="animate-spin text-[#1DB954]" />
            </div>
          ) : playlists.length === 0 ? (
            <p className="text-center text-white/40 py-8">Aucune playlist trouvee</p>
          ) : (
            <div className="space-y-2">
              {playlists.map((playlist) => (
                <button
                  key={playlist.id}
                  onClick={() => {
                    onPlaylistSelect(playlist);
                    setShowPlaylistSelector(false);
                  }}
                  className={`w-full p-3 rounded-xl flex items-center gap-3 transition-colors ${
                    selectedPlaylist?.id === playlist.id
                      ? "bg-[#1DB954]/20 border border-[#1DB954]"
                      : "bg-white/5 hover:bg-white/10"
                  }`}
                >
                  {playlist.image_url ? (
                    <img
                      src={playlist.image_url}
                      alt={playlist.name}
                      className="w-10 h-10 rounded object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded bg-white/10 flex items-center justify-center">
                      <Music size={16} className="text-white/40" />
                    </div>
                  )}
                  <div className="flex-1 text-left min-w-0">
                    <p className="font-medium truncate">{playlist.name}</p>
                    <p className="text-white/40 text-xs">{playlist.track_count} pistes</p>
                  </div>
                  {selectedPlaylist?.id === playlist.id && (
                    <Check size={16} className="text-[#1DB954]" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}