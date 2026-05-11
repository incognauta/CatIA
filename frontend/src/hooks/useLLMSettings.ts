import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export interface LLMSettings {
  id?: string;
  model: string;
  temperature: number;
  maxTokens: number;
}

export interface LLMDefaults {
  model: string;
  temperature: number;
  max_tokens: number;
  available_models: Array<{ value: string; label: string }>;
  temperature_range: {
    min: number;
    max: number;
    step: number;
  };
  max_tokens_range: {
    min: number;
    max: number;
    step: number;
  };
}

export function useLLMSettings() {
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [defaults, setDefaults] = useState<LLMDefaults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Obtener configuración actual y valores por defecto
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        
        // Obtener settings del usuario (crea si no existen)
        const settingsRes = await apiClient.get('/llm-settings/');
        setSettings({
          id: settingsRes.data.id,
          model: settingsRes.data.model,
          temperature: settingsRes.data.temperature,
          maxTokens: settingsRes.data.max_tokens,
        });

        // Obtener valores por defecto del sistema
        const defaultsRes = await apiClient.get('/llm-settings/defaults/');
        setDefaults(defaultsRes.data);
        
        setError(null);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Error cargando configuración';
        setError(message);
        console.error('Error fetching LLM settings:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  // Actualizar configuración
  const updateSettings = useCallback(async (newSettings: Partial<LLMSettings>) => {
    if (!settings?.id) {
      setError('Settings ID no disponible');
      return;
    }

    try {
      setSaving(true);
      const payload = {
        model: newSettings.model ?? settings.model,
        temperature: newSettings.temperature ?? settings.temperature,
        max_tokens: newSettings.maxTokens ?? settings.maxTokens,
      };

      const response = await apiClient.patch(`/llm-settings/${settings.id}/`, payload);
      
      setSettings({
        id: response.data.id,
        model: response.data.model,
        temperature: response.data.temperature,
        maxTokens: response.data.max_tokens,
      });
      setError(null);
      
      return response.data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error guardando configuración';
      setError(message);
      console.error('Error updating LLM settings:', err);
      throw err;
    } finally {
      setSaving(false);
    }
  }, [settings?.id]);

  // Resetear a valores por defecto
  const resetSettings = useCallback(async () => {
    if (!settings?.id) {
      setError('Settings ID no disponible');
      return;
    }

    try {
      setSaving(true);
      const response = await apiClient.post(`/llm-settings/reset/`);
      
      setSettings({
        id: response.data.id,
        model: response.data.model,
        temperature: response.data.temperature,
        maxTokens: response.data.max_tokens,
      });
      setError(null);
      
      return response.data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error reseteando configuración';
      setError(message);
      console.error('Error resetting LLM settings:', err);
      throw err;
    } finally {
      setSaving(false);
    }
  }, [settings?.id]);

  return {
    settings,
    defaults,
    loading,
    error,
    saving,
    updateSettings,
    resetSettings,
  };
}
