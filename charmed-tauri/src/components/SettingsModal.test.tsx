import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SettingsModal from '../components/SettingsModal';
import React from 'react';

// Mock Tauri API
const mockInvoke = vi.fn((cmd, args) => {
  if (cmd === 'spotify_login') {
    return Promise.resolve('https://accounts.spotify.com/authorize?mock=true');
  }
  if (cmd === 'spotify_callback') {
    return Promise.resolve({ access_token: 'mock_token' });
  }
  return Promise.resolve(null);
});

vi.mock('@tauri-apps/api/core', () => ({
  invoke: (cmd: string, args?: unknown) => mockInvoke(cmd, args),
}));

// Mock Tauri Opener Plugin
const mockOpenUrl = vi.fn(() => Promise.resolve());
vi.mock('@tauri-apps/plugin-opener', () => ({
  openUrl: (url: string) => mockOpenUrl(url),
}));

describe('SettingsModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly when open', () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    expect(screen.getByText((content, element) => {
      return element?.tagName.toLowerCase() === 'h2' && content.includes('Configuration');
    })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Client ID/i)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <SettingsModal 
        isOpen={false} 
        onClose={() => {}} 
      />
    );
    
    expect(screen.queryByText(/Spotify Configuration/i)).not.toBeInTheDocument();
  });

  it('handles input changes for clientId', () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    expect(clientIdInput).toHaveValue('test-client-id');
  });

  it('handles input changes for clientSecret', () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    expect(clientSecretInput).toHaveValue('test-secret');
  });

  it('disables connect button when inputs are empty', () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    expect(connectButton).toBeDisabled();
  });

  it('enables connect button when inputs are filled', () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    expect(connectButton).not.toBeDisabled();
  });

  it('calls handleLogin and shows auth code input after clicking connect', async () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    // Fill inputs
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    // Click connect
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    fireEvent.click(connectButton);
    
    // Wait for async operations
    await waitFor(() => {
      expect(mockInvoke).toHaveBeenCalledWith('spotify_login', {
        clientId: 'test-client-id',
        clientSecret: 'test-secret',
      });
    });
    
    await waitFor(() => {
      expect(mockOpenUrl).toHaveBeenCalledWith('https://accounts.spotify.com/authorize?mock=true');
    });
    
    // Should show auth code input after successful login initiation
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/URL ou le code/i)).toBeInTheDocument();
    });
  });

  it('handles callback with auth code', async () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    // Fill inputs and connect
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    fireEvent.click(connectButton);
    
    // Wait for auth URL input to appear
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/URL ou le code/i)).toBeInTheDocument();
    });
    
    // Enter auth code
    const authCodeInput = screen.getByPlaceholderText(/URL ou le code/i);
    fireEvent.change(authCodeInput, { target: { value: 'test-auth-code' } });
    
    // Click validate
    const validateButton = screen.getByRole('button', { name: /Valider la connexion/i });
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(mockInvoke).toHaveBeenCalledWith('spotify_callback', { code: 'test-auth-code' });
    });
  });

  it('extracts code from URL in callback', async () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    // Fill inputs and connect
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    fireEvent.click(connectButton);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/URL ou le code/i)).toBeInTheDocument();
    });
    
    // Enter full URL with code
    const authCodeInput = screen.getByPlaceholderText(/URL ou le code/i);
    fireEvent.change(authCodeInput, { target: { value: 'http://localhost:8888/callback?code=extracted-code-123&state=xyz' } });
    
    const validateButton = screen.getByRole('button', { name: /Valider la connexion/i });
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(mockInvoke).toHaveBeenCalledWith('spotify_callback', { code: 'extracted-code-123' });
    });
  });

  it('handles login error', async () => {
    mockInvoke.mockImplementationOnce((cmd: string) => {
      if (cmd === 'spotify_login') {
        return Promise.reject(new Error('Login failed'));
      }
      return Promise.resolve(null);
    });
    
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    // Fill inputs
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    fireEvent.click(connectButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Erreur/i)).toBeInTheDocument();
    });
  });

  it('handles callback error', async () => {
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={() => {}} 
      />
    );
    
    // Fill inputs and connect
    const clientIdInput = screen.getByPlaceholderText(/Client ID/i);
    const clientSecretInput = screen.getByPlaceholderText(/Client Secret/i);
    fireEvent.change(clientIdInput, { target: { value: 'test-client-id' } });
    fireEvent.change(clientSecretInput, { target: { value: 'test-secret' } });
    
    const connectButton = screen.getByRole('button', { name: /Connecter Spotify/i });
    fireEvent.click(connectButton);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/URL ou le code/i)).toBeInTheDocument();
    });
    
    // Mock callback to fail
    mockInvoke.mockImplementationOnce((cmd: string) => {
      if (cmd === 'spotify_callback') {
        return Promise.reject(new Error('Callback failed'));
      }
      return Promise.resolve(null);
    });
    
    const authCodeInput = screen.getByPlaceholderText(/URL ou le code/i);
    fireEvent.change(authCodeInput, { target: { value: 'test-code' } });
    
    const validateButton = screen.getByRole('button', { name: /Valider la connexion/i });
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Erreur d'authentification/i)).toBeInTheDocument();
    });
  });

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn();
    render(
      <SettingsModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    );
    
    // Find the close button (X icon in top right)
    const closeButton = screen.getByRole('button', { name: '' });
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalled();
  });
});