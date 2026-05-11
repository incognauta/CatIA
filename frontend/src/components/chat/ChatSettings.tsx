import { useState, useEffect } from 'react';
import { useLLMSettings } from '../../hooks/useLLMSettings';

export function ChatSettings() {
  const {
    settings,
    defaults,
    loading,
    error,
    saving,
    updateSettings,
    resetSettings,
  } = useLLMSettings();

  const [tempSettings, setTempSettings] = useState<{
    model: string;
    temperature: number;
    maxTokens: number;
  } | null>(null);

  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Sincronizar tempSettings cuando settings carguen
  useEffect(() => {
    if (settings) {
      setTempSettings({
        model: settings.model,
        temperature: settings.temperature,
        maxTokens: settings.maxTokens,
      });
    }
  }, [settings]);

  const handleSave = async () => {
    if (!tempSettings) return;

    try {
      await updateSettings({
        model: tempSettings.model,
        temperature: tempSettings.temperature,
        maxTokens: tempSettings.maxTokens,
      });
      
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch {
      setShowError(true);
      setTimeout(() => setShowError(false), 3000);
    }
  };

  const handleReset = async () => {
    if (window.confirm('¿Estás seguro de que quieres resetear la configuración a valores por defecto?')) {
      try {
        await resetSettings();
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      } catch {
        setShowError(true);
        setTimeout(() => setShowError(false), 3000);
      }
    }
  };

  const hasChanges =
    tempSettings &&
    settings &&
    (tempSettings.model !== settings.model ||
      tempSettings.temperature !== settings.temperature ||
      tempSettings.maxTokens !== settings.maxTokens);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Cargando configuración...</div>
      </div>
    );
  }

  if (!tempSettings || !defaults) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-500">Error: No se pudo cargar la configuración</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">⚙️ Configuración LLM</h2>
          <p className="text-sm text-gray-600 mt-1">Personaliza cómo Groq genera respuestas</p>
        </div>

        {/* Error/Success Messages */}
        {showError && error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {showSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700">
            ✓ Configuración guardada correctamente
          </div>
        )}

        {/* Model Selection */}
        <div className="bg-white rounded-lg p-5 border border-gray-200">
          <div className="flex items-start justify-between mb-3">
            <div>
              <label className="block text-sm font-semibold text-gray-900">Modelo</label>
              <p className="text-xs text-gray-600 mt-1">Selecciona qué modelo de IA usará Groq</p>
            </div>
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
              {defaults.available_models.find((m) => m.value === tempSettings.model)?.label || tempSettings.model}
            </span>
          </div>

          <select
            value={tempSettings.model}
            onChange={(e) =>
              setTempSettings({ ...tempSettings, model: e.target.value })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {defaults.available_models.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label} ({model.value})
              </option>
            ))}
          </select>

          <div className="mt-3 text-xs text-gray-600 space-y-1">
            <p>📌 <strong>Modelos disponibles:</strong></p>
            <ul className="list-disc list-inside space-y-0.5">
              {defaults.available_models.map((model) => (
                <li key={model.value}>{model.label}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Temperature Slider */}
        <div className="bg-white rounded-lg p-5 border border-gray-200">
          <div className="flex items-start justify-between mb-3">
            <div>
              <label className="block text-sm font-semibold text-gray-900">Temperatura</label>
              <p className="text-xs text-gray-600 mt-1">Controla la creatividad (baja = predecible, alta = creativa)</p>
            </div>
            <span className="text-sm font-mono bg-blue-100 text-blue-700 px-3 py-1 rounded">
              {tempSettings.temperature.toFixed(2)}
            </span>
          </div>

          <input
            type="range"
            min={defaults.temperature_range.min}
            max={defaults.temperature_range.max}
            step={defaults.temperature_range.step}
            value={tempSettings.temperature}
            onChange={(e) =>
              setTempSettings({ ...tempSettings, temperature: parseFloat(e.target.value) })
            }
            className="w-full h-2 bg-gradient-to-r from-blue-400 to-purple-600 rounded-lg appearance-none cursor-pointer"
          />

          <div className="mt-3 flex justify-between text-xs text-gray-600">
            <span>❄️ Determinista</span>
            <span>🔥 Creativo</span>
          </div>

          <div className="mt-3 text-xs text-gray-600 space-y-1">
            <p>💡 <strong>Guía:</strong></p>
            <ul className="list-disc list-inside space-y-0.5">
              <li>0.0-0.3: Respuestas precisas y consistentes</li>
              <li>0.4-0.6: Balance entre precisión y variedad</li>
              <li>0.7-1.0: Respuestas más creativas y variadas</li>
            </ul>
          </div>
        </div>

        {/* Max Tokens Input */}
        <div className="bg-white rounded-lg p-5 border border-gray-200">
          <div className="flex items-start justify-between mb-3">
            <div>
              <label className="block text-sm font-semibold text-gray-900">Máximo de Tokens</label>
              <p className="text-xs text-gray-600 mt-1">Longitud máxima de la respuesta (1 token ≈ 4 caracteres)</p>
            </div>
            <span className="text-sm font-mono bg-green-100 text-green-700 px-3 py-1 rounded">
              {tempSettings.maxTokens}
            </span>
          </div>

          <input
            type="range"
            min={defaults.max_tokens_range.min}
            max={defaults.max_tokens_range.max}
            step={defaults.max_tokens_range.step}
            value={tempSettings.maxTokens}
            onChange={(e) =>
              setTempSettings({ ...tempSettings, maxTokens: parseInt(e.target.value, 10) })
            }
            className="w-full h-2 bg-gradient-to-r from-green-400 to-emerald-600 rounded-lg appearance-none cursor-pointer"
          />

          <div className="mt-3 flex justify-between text-xs text-gray-600">
            <span>📝 Corto</span>
            <span>📚 Largo</span>
          </div>

          <div className="mt-3 text-xs text-gray-600 space-y-1">
            <p>💡 <strong>Estimación:</strong></p>
            <ul className="list-disc list-inside space-y-0.5">
              <li>256-512 tokens: ~1-2 párrafos</li>
              <li>1024-2048 tokens: ~3-8 párrafos</li>
              <li>2048+ tokens: Respuestas muy largas</li>
            </ul>
          </div>
        </div>

        {/* Sistema Defaults Info */}
        {defaults && (
          <div className="bg-gray-100 rounded-lg p-4 text-xs text-gray-700 space-y-2">
            <p className="font-semibold">📋 Valores por Defecto del Sistema:</p>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <p className="text-gray-600">Modelo</p>
                <p className="font-mono">{defaults.model}</p>
              </div>
              <div>
                <p className="text-gray-600">Temperatura</p>
                <p className="font-mono">{defaults.temperature}</p>
              </div>
              <div>
                <p className="text-gray-600">Max Tokens</p>
                <p className="font-mono">{defaults.max_tokens}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="border-t border-gray-200 bg-white p-4 flex gap-3">
        <button
          onClick={handleReset}
          disabled={saving}
          className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          🔄 Reset
        </button>
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className="flex-1 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {saving ? '⏳ Guardando...' : '💾 Guardar'}
        </button>
      </div>
    </div>
  );
}
