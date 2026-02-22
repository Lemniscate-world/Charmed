import { useState } from "react";
import { ExternalLink, Check, ChevronRight, ChevronLeft } from "lucide-react";

interface SetupGuideProps {
  onComplete: () => void;
}

export default function SetupGuide({ onComplete }: SetupGuideProps) {
  const [step, setStep] = useState(0);
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");

  const steps = [
    {
      title: "Bienvenue sur Charmed",
      description: "Charmed est un reveil Spotify premium. Pour fonctionner, il needs access to your Spotify account.",
      content: (
        <div className="space-y-4">
          <p className="text-white/60">
            Cette configuration ne prendra que quelques minutes. Vous aurez besoin de:
          </p>
          <ul className="list-disc list-inside text-white/40 space-y-2">
            <li>Un compte Spotify Premium</li>
            <li>Acces au <a href="https://developer.spotify.com/dashboard" target="_blank" rel="noopener noreferrer" className="text-[#1DB954] hover:underline">Spotify Developer Dashboard</a></li>
          </ul>
        </div>
      ),
    },
    {
      title: "Creer une application Spotify",
      description: "Sur le Spotify Developer Dashboard, creez une nouvelle application.",
      content: (
        <div className="space-y-4">
          <ol className="list-decimal list-inside text-white/60 space-y-3">
            <li>
              Allez sur{" "}
              <a 
                href="https://developer.spotify.com/dashboard" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-[#1DB954] hover:underline inline-flex items-center gap-1"
              >
                Spotify Developer Dashboard
                <ExternalLink size={14} />
              </a>
            </li>
            <li>Cliquez sur "Create App"</li>
            <li>Remplissez les informations:
              <ul className="list-disc list-inside ml-6 mt-2 text-white/40">
                <li><strong>App name</strong>: Charmed</li>
                <li><strong>App description</strong>: Spotify Alarm Clock</li>
                <li><strong>Redirect URI</strong>: http://localhost:8888/callback</li>
              </ul>
            </li>
            <li>Cochez "I understand and agree..." et cliquez "Save"</li>
          </ol>
        </div>
      ),
    },
    {
      title: "Configurer les Redirect URIs",
      description: "Ajoutez l'URL de redirection dans les parametres de l'application.",
      content: (
        <div className="space-y-4">
          <ol className="list-decimal list-inside text-white/60 space-y-3">
            <li>Dans votre application Spotify, allez dans <strong>Settings</strong></li>
            <li>Scrollez jusqu'a <strong>Redirect URIs</strong></li>
            <li>Cliquez "Add URI" et entrez:</li>
          </ol>
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 font-mono text-sm">
            http://localhost:8888/callback
          </div>
          <p className="text-white/40 text-sm">
            Cette URL est utilisee pour recevoir le code d'autorisation apres la connexion Spotify.
          </p>
        </div>
      ),
    },
    {
      title: "Copier les identifiants",
      description: "Recuperez votre Client ID et Client Secret.",
      content: (
        <div className="space-y-4">
          <ol className="list-decimal list-inside text-white/60 space-y-3">
            <li>Dans les settings de votre application Spotify</li>
            <li>Vous verrez <strong>Client ID</strong> - copiez-le</li>
            <li>Cliquez "View client secret" et copiez-le aussi</li>
          </ol>
          
          <div className="space-y-3 mt-4">
            <div>
              <label className="text-sm text-white/60 block mb-2">Client ID</label>
              <input
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="Collez votre Client ID ici"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 outline-none focus:border-[#1DB954]"
              />
            </div>
            <div>
              <label className="text-sm text-white/60 block mb-2">Client Secret</label>
              <input
                type="password"
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
                placeholder="Collez votre Client Secret ici"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 outline-none focus:border-[#1DB954]"
              />
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Configuration terminee!",
      description: "Vos identifiants sont prets. Vous pouvez maintenant connecter Spotify.",
      content: (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-[#1DB954]/10 border border-[#1DB954]/20 rounded-xl">
            <Check size={24} className="text-[#1DB954]" />
            <div>
              <p className="font-medium">Configuration enregistree</p>
              <p className="text-white/40 text-sm">Client ID: {clientId.substring(0, 8)}...</p>
            </div>
          </div>
          
          <p className="text-white/60">
            Au prochain lancement, cliquez sur "Connecter Spotify" dans les parametres pour autoriser l'acces a votre compte.
          </p>
          
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <p className="text-white/40 text-sm">
              <strong>Conseil:</strong> Gardez vos identifiants secrets. Ne les partagez jamais publiquement.
            </p>
          </div>
        </div>
      ),
    },
  ];

  const currentStep = steps[step];
  const isLastStep = step === steps.length - 1;
  const isFirstStep = step === 0;

  const handleNext = () => {
    if (isLastStep) {
      onComplete();
    } else {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md">
      <div className="glass-panel w-full max-w-lg p-8 relative">
        {/* Progress indicator */}
        <div className="flex items-center gap-2 mb-6">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-1 flex-1 rounded-full transition-colors ${
                i <= step ? "bg-[#1DB954]" : "bg-white/10"
              }`}
            />
          ))}
        </div>

        <h2 className="text-2xl font-bold mb-2">{currentStep.title}</h2>
        <p className="text-white/40 mb-6">{currentStep.description}</p>

        <div className="min-h-[200px]">{currentStep.content}</div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
          <button
            onClick={handleBack}
            disabled={isFirstStep}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-colors ${
              isFirstStep
                ? "text-white/20 cursor-not-allowed"
                : "text-white/60 hover:text-white hover:bg-white/5"
            }`}
          >
            <ChevronLeft size={18} />
            Retour
          </button>

          <button
            onClick={handleNext}
            disabled={step === 3 && (!clientId || !clientSecret)}
            className={`flex items-center gap-2 px-6 py-2 rounded-xl font-semibold transition-all ${
              step === 3 && (!clientId || !clientSecret)
                ? "bg-white/10 text-white/30 cursor-not-allowed"
                : "bg-[#1DB954] text-black hover:bg-[#19a34a]"
            }`}
          >
            {isLastStep ? "Terminer" : "Suivant"}
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}