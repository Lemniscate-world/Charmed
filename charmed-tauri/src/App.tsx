import { useState, useEffect, useCallback, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Bell, Settings, Music2, Plus, Trash2, Power } from "lucide-react";
import "./index.css";
import SettingsModal from "./components/SettingsModal";

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

export default function App() {
  const [time, setTime] = useState("00:00:00");
  const [alarmTime, setAlarmTime] = useState("08:00");
  const [alarms, setAlarms] = useState<AlarmEntry[]>([]);
  const [isSettingAlarm, setIsSettingAlarm] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [triggeredAlarm, setTriggeredAlarm] = useState<AlarmEntry | null>(null);
  const lastTriggeredRef = useRef<string | null>(null);

  // Horloge temps réel via Rust IPC
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const t = await invoke<string>("get_current_time");
        setTime(t);
      } catch {
        // Fallback JS si Rust pas encore prêt
        setTime(new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Vérification des alarmes toutes les secondes
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

  // Rafraîchir la liste des alarmes
  const refreshAlarms = useCallback(async () => {
    try {
      const list = await invoke<AlarmEntry[]>("get_alarms");
      setAlarms(list);
    } catch { /* silencieux */ }
  }, []);

  // Créer une alarme
  const handleSetAlarm = async () => {
    try {
      await invoke("set_alarm", {
        time: alarmTime,
        playlistName: "Morning Mix",
        playlistUri: "spotify:playlist:default",
        volume: 80,
        days: [],
        fadeIn: false,
        fadeInDuration: 10,
      });
      await refreshAlarms();
      setIsSettingAlarm(false);
    } catch (e) {
      console.error("Erreur IPC:", e);
    }
  };

  const handleStopAlarm = async () => {
    try {
      await invoke("stop_local_alarm");
    } catch {}
    setTriggeredAlarm(null);
  };

  // Activer/Désactiver une alarme
  const handleToggle = async (id: string) => {
    try {
      await invoke("toggle_alarm", { alarmId: id });
      await refreshAlarms();
    } catch (e) {
      console.error("Erreur toggle:", e);
    }
  };

  // Supprimer une alarme
  const handleDelete = async (id: string) => {
    try {
      await invoke("delete_alarm", { alarmId: id });
      await refreshAlarms();
    } catch (e) {
      console.error("Erreur delete:", e);
    }
  };

  const hasActiveAlarm = alarms.some((a) => a.active);

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center p-6 gradient-bg">
      {/* Halos floutés animés */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#1DB954] rounded-full filter blur-[120px] opacity-20 animate-blob"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#A238FF] rounded-full filter blur-[120px] opacity-15 animate-blob" style={{ animationDelay: "2s" }}></div>

      {/* Alerte si alarme déclenchée */}
      {triggeredAlarm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md">
          <div className="glass-panel p-12 text-center animate-pulse">
            <Bell size={64} className="text-[#1DB954] mx-auto mb-6" />
            <h2 className="text-4xl font-bold mb-2">ALARME !</h2>
            <p className="text-white/60 text-xl">{triggeredAlarm.playlist_name}</p>
            <button onClick={handleStopAlarm} className="mt-8 px-8 py-3 rounded-full bg-red-500 hover:bg-red-600 text-white font-semibold transition-all">
              Arrêter
            </button>
          </div>
        </div>
      )}

      {/* Conteneur principal */}
      <div className="glass-panel w-full max-w-4xl h-[80vh] flex overflow-hidden relative z-10">

        <SettingsModal 
          isOpen={isSettingsOpen} 
          onClose={() => setIsSettingsOpen(false)} 
        />

        {/* Sidebar */}
        <div className="w-24 border-r border-white/5 flex flex-col items-center py-8 gap-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#1DB954] to-[#14833b] flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform cursor-pointer">
            <Music2 size={24} className="text-black" />
          </div>
          <div className="flex-1 flex flex-col justify-center gap-6">
            <button className="p-3 rounded-xl hover:bg-white/5 text-white/50 hover:text-white transition-colors" title="Alarmes">
              <Bell size={24} />
            </button>
            <button onClick={() => setIsSettingAlarm(!isSettingAlarm)} className="p-3 rounded-xl hover:bg-white/5 text-white/50 hover:text-[#1DB954] transition-colors" title="Ajouter">
              <Plus size={24} />
            </button>
            <button onClick={() => setIsSettingsOpen(true)} className="p-3 rounded-xl hover:bg-white/5 text-white/50 hover:text-white transition-colors" title="Paramètres">
              <Settings size={24} />
            </button>
          </div>
        </div>

        {/* Zone principale */}
        <div className="flex-1 p-12 flex flex-col justify-between overflow-y-auto">

          <header className="flex justify-between items-start">
            <div>
              <h1 className="text-5xl font-light tracking-tight">Bonjour, Kuro.</h1>
              <p className="text-white/40 mt-2 text-lg font-light">Prêt à dominer la journée.</p>
            </div>
            <div className="glass-button px-6 py-2 rounded-full flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${hasActiveAlarm ? "bg-[#1DB954] shadow-[0_0_10px_#1DB954]" : "bg-red-500"}`}></div>
              <span className="text-sm font-medium tracking-wide">{hasActiveAlarm ? "ALARME ACTIVE" : "REPOS"}</span>
            </div>
          </header>

          <main className="flex flex-col items-center justify-center flex-1">
            <h2 className="text-[100px] font-bold tracking-tighter leading-none glow-text text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60">
              {time}
            </h2>

            {/* Formulaire rapide d'alarme */}
            <div className="mt-12 flex items-center gap-4 p-2 rounded-full glass-button">
              <input
                type="time"
                value={alarmTime}
                onChange={(e) => setAlarmTime(e.target.value)}
                className="bg-transparent border-none text-2xl font-light outline-none text-center text-white px-4 py-2"
              />
              <button
                onClick={handleSetAlarm}
                className="w-14 h-14 rounded-full flex items-center justify-center bg-[#1DB954] hover:bg-[#19a34a] text-black shadow-lg transition-all hover:scale-105"
              >
                <Plus size={24} />
              </button>
            </div>
          </main>

          {/* Liste des alarmes programmées */}
          {alarms.length > 0 && (
            <footer className="space-y-3 mt-6">
              <h3 className="text-white/30 text-xs uppercase tracking-widest font-semibold mb-2">Alarmes Programmées</h3>
              {alarms.map((alarm) => (
                <div key={alarm.id} className="glass-button rounded-2xl p-4 flex items-center gap-4">
                  <div className={`text-3xl font-light flex-1 ${alarm.active ? "text-white" : "text-white/30 line-through"}`}>
                    {alarm.time}
                  </div>
                  <span className="text-white/40 text-sm">{alarm.playlist_name}</span>
                  <button onClick={() => handleToggle(alarm.id)} className={`p-2 rounded-lg transition-colors ${alarm.active ? "text-[#1DB954] hover:bg-white/5" : "text-white/30 hover:bg-white/5"}`}>
                    <Power size={18} />
                  </button>
                  <button onClick={() => handleDelete(alarm.id)} className="p-2 rounded-lg text-red-400/60 hover:text-red-400 hover:bg-white/5 transition-colors">
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </footer>
          )}
        </div>
      </div>
    </div>
  );
}
