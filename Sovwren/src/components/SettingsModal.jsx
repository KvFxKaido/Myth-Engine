import { X, Save, Key } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getKeyStatus, setKeys as saveKeys } from '../services/api';

export default function SettingsModal({ isOpen, onClose }) {
    const [keys, setKeys] = useState({
        gemini: '',
        claude: '',
        openai: ''
    });
    const [status, setStatus] = useState({ gemini: false, claude: false, openai: false });
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isOpen) {
            setError(null);
            setKeys({ gemini: '', claude: '', openai: '' });
            getKeyStatus().then(setStatus).catch(() => setStatus({ gemini: false, claude: false, openai: false }));
        }
    }, [isOpen]);

    const handleSave = async () => {
        setError(null);
        try {
            await saveKeys(keys);
            const updated = await getKeyStatus();
            setStatus(updated);
            onClose();
        } catch (e) {
            setError(e?.message || 'Failed to save keys');
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="w-full max-w-md bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl overflow-hidden">
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/5">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Key size={18} className="text-purple-400" />
                        API Settings
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    <p className="text-sm text-gray-400 mb-4">
                        Keys are stored in your local Sovwren backend (not in browser storage) and are only sent to the provider you choose.
                    </p>
                    <p className="text-xs text-gray-500">
                        Status: Gemini {status.gemini ? 'configured' : 'missing'} | Claude {status.claude ? 'configured' : 'missing'} | OpenAI {status.openai ? 'configured' : 'missing'}
                    </p>
                    {error && (
                        <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                            {error}
                        </p>
                    )}

                    <div className="space-y-2">
                        <label className="text-xs font-medium text-gray-300 uppercase tracking-wider">Google Gemini API Key</label>
                        <input
                            type="password"
                            value={keys.gemini}
                            onChange={(e) => setKeys({ ...keys, gemini: e.target.value })}
                            placeholder="AIzaSy..."
                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all placeholder-gray-600"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-medium text-gray-300 uppercase tracking-wider">Anthropic API Key</label>
                        <input
                            type="password"
                            value={keys.claude}
                            onChange={(e) => setKeys({ ...keys, claude: e.target.value })}
                            placeholder="sk-ant-..."
                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all placeholder-gray-600"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-medium text-gray-300 uppercase tracking-wider">OpenAI API Key</label>
                        <input
                            type="password"
                            value={keys.openai}
                            onChange={(e) => setKeys({ ...keys, openai: e.target.value })}
                            placeholder="sk-..."
                            className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2.5 text-gray-200 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 transition-all placeholder-gray-600"
                        />
                    </div>
                </div>

                <div className="px-6 py-4 bg-white/5 border-t border-white/5 flex justify-end">
                    <button
                        onClick={handleSave}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors shadow-lg shadow-purple-500/20"
                    >
                        <Save size={18} />
                        Save Keys
                    </button>
                </div>
            </div>
        </div>
    );
}
