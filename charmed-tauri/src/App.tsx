import { useState, useEffect, useCallback, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { openUrl } from "@tauri-apps/plugin-opener";
import { Bell, Music2, Plus, Trash2, Power, ExternalLink, Check, Loader2 } from "lucide-react";
import "./index.css";

// Type miroir de la struct Rust AlarmEntry
interface AlarmEntry {
  id: string;
  time: string;
  playlist_name: string;
  playlist_uri: string;
  volume: number;
  active: boolean;
  days: string[];
  fade_in: boolean;
  fade_in_duration: number;
}

// Type miroir de la struct Rust SpotifyPlaylist
interface SpotifyPlaylist {
  id: string;
  name: string;
  uri: string;
  image_url: string | null;
  track_count: number;
  owner: string;
}

export default function App() {
  const [time, setTime] = useState("00:00:00");
  const [alarmTime, setAlarmTime] = useState("08:00");
  const [alarms, setAlarms] = useState<AlarmEntry[]>([]);
  const [triggeredAlarm, setTriggeredAlarm] = useState<AlarmEntry | null>(null);
  const lastTriggeredRef = useRef<string | null>(null);

  // Spotify state
  const [isSpotifyAuthenticated, setIsSpotifyAuthenticated] = useState(false);
  const [playlists, setPlaylists] = useState<SpotifyPlaylist[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState<SpotifyPlaylist | null>(null);
  const [showSpotifyConnect, setShowSpotifyConnect] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [callbackCode, setCallbackCode] = useState("");
  const [showCodeInput, setShowCodeInput] = useState(false);
  const [clientIdInput, setClientIdInput] = useState("");
  const [showClientIdInput, setShowClientIdInput] = useState(false);

  // Charger les données au démarrage
  useEffect(() => {
    refreshAlarms();
    checkSpotifyAuth();
  }, []);

  // Vérifier l'authentification Spotify
  const checkSpotifyAuth = async () => {
    try {
      const auth = await invoke<boolean>("is_spotify_authenticated");
      setIsSpotifyAuthenticated(auth);
      if (auth) {
        await loadPlaylists();
      }
    } catch {
      // Pas encore authentifié
    }
  };

  // Charger les playlists Spotify
  const loadPlaylists = async () => {
    try {
      const list = await invoke<SpotifyPlaylist[]>("get_spotify_playlists");
      setPlaylists(list);
    } catch {
      // Silencieux
    }
  };

  // Horloge temps réel
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const t = await invoke<string>("get_current_time");
        setTime(t);
      } catch {
        setTime(new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Vérification des alarmes
  useEffect(() => {
    const checker = setInterval(async () => {
      try {
        const triggered = await invoke<AlarmEntry | null>("check_alarms");
        if (triggered) {
          const now = new Date();
          const dateKey = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
          const key = `${triggered.id}-${triggered.time}-${dateKey}`;
          if (lastTriggeredRef.current !== key) {
            lastTriggeredRef.current = key;
            setTriggeredAlarm(triggered);
            try {
              await invoke("play_local_alarm");
            } catch {}
            setTimeout(() => setTriggeredAlarm(null), 30000);
          }
        }
      } catch {}
    }, 1000);
    return () => clearInterval(checker);
  }, []);

  // Rafraîchir les alarmes
  const refreshAlarms = useCallback(async () => {
    try {
      const list = await invoke<AlarmEntry[]>("get_alarms");
      setAlarms(list);
    } catch {}
  }, []);

  // Créer une alarme
  const handleSetAlarm = async () => {
    try {
      await invoke("set_alarm", {
        time: alarmTime,
        playlistName: selectedPlaylist?.name || "Alarme",
        playlistUri: selectedPlaylist?.uri || "local",
        volume: 80,
        days: [],
        fadeIn: false,
        fadeInDuration: 10,
      });
      await refreshAlarms();
      setAlarmTime("08:00");
    } catch (e) {
      console.error("Erreur création alarme:", e);
    }
  };

  // Toggle alarme
  const handleToggle = async (id: string) => {
    try {
      await invoke("toggle_alarm", { alarmId: id });
      await refreshAlarms();
    } catch (e) {
      console.error("Erreur toggle:", e);
    }
  };

  // Supprimer alarme
  const handleDelete = async (id: string) => {
    try {
      await invoke("delete_alarm", { alarmId: id });
      await refreshAlarms();
    } catch (e) {
      console.error("Erreur suppression:", e);
    }
  };

  // Arrêter l'alarme
  const handleStopAlarm = async () => {
    try {
      await invoke("stop_local_alarm");
    } catch {}
    setTriggeredAlarm(null);
  };

  // Étape 1: Demander le Client ID
  const handleSpotifyLogin = async () => {
    setShowClientIdInput(true);
  };

  // Étape 2: Lancer OAuth avec le Client ID
  const handleStartOAuth = async () => {
    if (!clientIdInput.trim()) return;
    
    setIsLoading(true);
    try {
      const authUrl = await invoke<string>("spotify_login", {
        clientId: clientIdInput,
        clientSecret: "",
      });

      // Ouvrir automatiquement Spotify dans le navigateur
      await openUrl(authUrl);
      setShowClientIdInput(false);
      setShowCodeInput(true);
    } catch (e) {
      console.error("Erreur login Spotify:", e);
      alert("Erreur: " + e);
    } finally {
      setIsLoading(false);
    }
  };

  // Valider le code OAuth
  const handleCallback = async () => {
    if (!callbackCode.trim()) return;
    
    setIsLoading(true);
    try {
      let code = callbackCode;
      if (callbackCode.includes("code=")) {
        const match = callbackCode.match(/code=([^&]+)/);
        if (match) code = match[1];
      }

      await invoke("spotify_callback", { code });
      setIsSpotifyAuthenticated(true);
      setShowCodeInput(false);
      setShowSpotifyConnect(false);
      setCallbackCode("");
      await loadPlaylists();
    } catch (e) {
      console.error("Erreur callback:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const hasActiveAlarm = alarms.some((a) => a.active);

  return (
    <div className="min-h-screen w-full gradient-bg flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#1DB954] rounded-full filter blur-[150px] opacity-20"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-[150px] opacity-15"></div>
      </div>

      {/* Alarm triggered overlay */}
      {triggeredAlarm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-xl">
          <div className="text-center p-12">
            <div className="w-32 h-32 mx-auto mb-8 rounded-full bg-[#1DB954] flex items-center justify-center animate-pulse">
              <Bell size={64} className="text-black" />
            </div>
            <h2 className="text-6xl font-bold mb-4">ALARME</h2>
            <p className="text-2xl text-white/60 mb-8">{triggeredAlarm.time}</p>
            <button
              onClick={handleStopAlarm}
              className="px-12 py-4 rounded-full bg-white text-black font-bold text-xl hover:bg-gray-100 transition-colors"
            >
              Arrêter
            </button>
          </div>
        </div>
      )}

      {/* Main container */}
      <div className="relative z-10 w-full max-w-5xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#1DB954] to-[#1ed760] flex items-center justify-center shadow-lg">
              <Music2 size={28} className="text-black" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Charmed</h1>
              <p className="text-white/40">Spotify Alarm Clock</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${hasActiveAlarm ? "bg-[#1DB954]/20 text-[#1DB954]" : "bg-white/5 text-white/40"}`}>
              <div className={`w-2 h-2 rounded-full ${hasActiveAlarm ? "bg-[#1DB954]" : "bg-white/20"}`}></div>
              <span className="text-sm font-medium">{hasActiveAlarm ? "Actif" : "Inactif"}</span>
            </div>
            
            {/* Spotify connect button */}
            <button
              onClick={() => setShowSpotifyConnect(!showSpotifyConnect)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full transition-colors ${isSpotifyAuthenticated ? "bg-[#1DB954]/20 text-[#1DB954]" : "bg-white/5 text-white/60 hover:bg-white/10"}`}
            >
              {isSpotifyAuthenticated ? <Check size={18} /> : <ExternalLink size={18} />}
              <span className="text-sm font-medium">{isSpotifyAuthenticated ? "Spotify connecté" : "Connecter Spotify"}</span>
            </button>
          </div>
        </div>

        {/* Spotify connection panel */}
        {showSpotifyConnect && !isSpotifyAuthenticated && (
          <div className="glass-panel rounded-3xl p-8 mb-8">
            <h3 className="text-xl font-semibold mb-4">Connecter Spotify</h3>
            
            {!showClientIdInput && !showCodeInput ? (
              <>
                <p className="text-white/40 mb-6">
                  Connectez votre compte Spotify pour utiliser vos playlists comme sonneries d'alarme.
                </p>
                <button
                  onClick={handleSpotifyLogin}
                  className="w-full py-4 rounded-2xl bg-[#1DB954] hover:bg-[#1ed760] text-black font-semibold flex items-center justify-center gap-2 transition-colors"
                >
                  <ExternalLink size={20} />
                  Commencer la configuration
                </button>
              </>
            ) : showClientIdInput && !showCodeInput ? (
              <>
                <p className="text-white/40 mb-4">
                  Vous devez créer une application Spotify pour obtenir un Client ID:
                </p>
                <ol className="list-decimal list-inside text-white/60 space-y-2 mb-6 text-sm">
                  <li>
                    Allez sur{" "}
                    <a 
                      href="https://developer.spotify.com/dashboard" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[#1DB954] hover:underline"
                    >
                      developer.spotify.com/dashboard
                    </a>
                  </li>
                  <li>Cliquez "Create App" puis remplissez les infos</li>
                  <li>Copiez le <strong>Client ID</strong> ci-dessous</li>
                </ol>
                <div className="space-y-4">
                  <input
                    type="text"
                    value={clientIdInput}
                    onChange={(e) => setClientIdInput(e.target.value)}
                    placeholder="Collez votre Client ID ici"
                    className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white outline-none focus:border-[#1DB954]"
                  />
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowClientIdInput(false)}
                      className="flex-1 py-3 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      Annuler
                    </button>
                    <button
                      onClick={handleStartOAuth}
                      disabled={isLoading || !clientIdInput.trim()}
                      className="flex-1 py-3 rounded-2xl bg-[#1DB954] text-black font-semibold flex items-center justify-center gap-2"
                    >
                      {isLoading ? <Loader2 size={18} className="animate-spin" /> : <ExternalLink size={18} />}
                      Continuer
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-white/60">
                  Une page Spotify s'est ouverte. Après autorisation, copiez l'URL de redirection ou le code:
                </p>
                <input
                  type="text"
                  value={callbackCode}
                  onChange={(e) => setCallbackCode(e.target.value)}
                  placeholder="Collez l'URL ou le code ici"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-white outline-none focus:border-[#1DB954]"
                />
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowCodeInput(false)}
                    className="flex-1 py-3 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleCallback}
                    disabled={isLoading || !callbackCode}
                    className="flex-1 py-3 rounded-2xl bg-[#1DB954] text-black font-semibold flex items-center justify-center gap-2"
                  >
                    {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Check size={18} />}
                    Valider
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Clock */}
        <div className="text-center mb-12">
          <h2 className="text-[120px] font-bold tracking-tighter leading-none text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">
            {time}
          </h2>
          <p className="text-white/40 text-lg mt-2">
            {new Date().toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" })}
          </p>
        </div>

        {/* Add alarm */}
        <div className="glass-panel rounded-3xl p-6 mb-8">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="text-white/40 text-sm mb-2 block">Heure de l'alarme</label>
              <input
                type="time"
                value={alarmTime}
                onChange={(e) => setAlarmTime(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-3xl text-white outline-none focus:border-[#1DB954] transition-colors w-full"
              />
            </div>
            
            {isSpotifyAuthenticated && playlists.length > 0 && (
              <div className="flex-1">
                <label className="text-white/40 text-sm mb-2 block">Playlist (optionnel)</label>
                <select
                  value={selectedPlaylist?.id || ""}
                  onChange={(e) => {
                    const playlist = playlists.find(p => p.id === e.target.value);
                    setSelectedPlaylist(playlist || null);
                  }}
                  className="bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white outline-none focus:border-[#1DB954] transition-colors w-full"
                >
                  <option value="" className="bg-gray-800">Sélectionner une playlist</option>
                  {playlists.map((p) => (
                    <option key={p.id} value={p.id} className="bg-gray-800">{p.name}</option>
                  ))}
                </select>
              </div>
            )}
            
            <button
              onClick={handleSetAlarm}
              className="h-[72px] w-[72px] rounded-2xl bg-[#1DB954] hover:bg-[#1ed760] text-black flex items-center justify-center transition-all hover:scale-105 shadow-lg"
            >
              <Plus size={32} />
            </button>
          </div>
        </div>

        {/* Alarms list */}
        {alarms.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-white/40 text-sm font-medium px-2">Mes alarmes</h3>
            {alarms.map((alarm) => (
              <div
                key={alarm.id}
                className="glass-panel rounded-2xl p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
              >
                <div className={`text-4xl font-light ${alarm.active ? "text-white" : "text-white/30 line-through"}`}>
                  {alarm.time}
                </div>
                <div className="flex-1 text-white/40 text-sm">
                  {alarm.playlist_name}
                </div>
                <button
                  onClick={() => handleToggle(alarm.id)}
                  className={`p-3 rounded-xl transition-colors ${alarm.active ? "bg-[#1DB954]/20 text-[#1DB954]" : "bg-white/5 text-white/30"}`}
                >
                  <Power size={20} />
                </button>
                <button
                  onClick={() => handleDelete(alarm.id)}
                  className="p-3 rounded-xl bg-white/5 text-red-400/60 hover:text-red-400 hover:bg-red-400/10 transition-colors"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {alarms.length === 0 && (
          <div className="text-center py-12">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
              <Bell size={32} className="text-white/20" />
            </div>
            <p className="text-white/40">Aucune alarme programmée</p>
            <p className="text-white/20 text-sm mt-1">Définissez une heure ci-dessus pour créer une alarme</p>
          </div>
        )}
      </div>
    </div>
  );
}