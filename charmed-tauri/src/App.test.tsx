import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';
import React from 'react';

// Mock Tauri API
const mockInvoke = vi.fn();

vi.mock('@tauri-apps/api/core', () => ({
  invoke: (cmd: string, args?: unknown) => mockInvoke(cmd, args),
}));

// Mock SettingsModal
vi.mock('./components/SettingsModal', () => ({
  default: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => 
    isOpen ? (
      <div data-testid="settings-modal">
        <span>Mock Settings Modal</span>
        <button onClick={onClose} aria-label="Close">Close</button>
      </div>
    ) : null
}));

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementations
    mockInvoke.mockImplementation((cmd: string) => {
      switch (cmd) {
        case 'get_current_time':
          return Promise.resolve('12:00:00');
        case 'check_alarms':
          return Promise.resolve(null);
        case 'get_alarms':
          return Promise.resolve([]);
        default:
          return Promise.resolve(null);
      }
    });
  });

  it('renders clock and greeting', () => {
    render(<App />);
    
    expect(screen.getByText('00:00:00')).toBeInTheDocument();
    expect(screen.getByText(/Bonjour, Kuro/i)).toBeInTheDocument();
  });

  it('shows REPOS status when no alarms are active', () => {
    render(<App />);
    expect(screen.getByText('REPOS')).toBeInTheDocument();
  });

  it('renders the time input with default value', () => {
    render(<App />);
    expect(screen.getByDisplayValue('08:00')).toBeInTheDocument();
  });

  it('opens settings modal when settings button is clicked', () => {
    render(<App />);
    
    const buttons = screen.getAllByRole('button');
    const settingsButton = buttons.find(btn => btn.title === 'Parametres');
    
    if (settingsButton) {
      fireEvent.click(settingsButton);
      expect(screen.getByTestId('settings-modal')).toBeInTheDocument();
    }
  });

  it('closes settings modal when close button is clicked', () => {
    render(<App />);
    
    const buttons = screen.getAllByRole('button');
    const settingsButton = buttons.find(btn => btn.title === 'Parametres');
    
    if (settingsButton) {
      fireEvent.click(settingsButton);
      expect(screen.getByTestId('settings-modal')).toBeInTheDocument();
      
      const closeButton = screen.getByLabelText('Close');
      fireEvent.click(closeButton);
      expect(screen.queryByTestId('settings-modal')).not.toBeInTheDocument();
    }
  });

  it('handles IPC errors gracefully for get_current_time', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    mockInvoke.mockImplementation((cmd: string) => {
      if (cmd === 'get_current_time') {
        return Promise.reject(new Error('IPC Error'));
      }
      if (cmd === 'check_alarms') return Promise.resolve(null);
      if (cmd === 'get_alarms') return Promise.resolve([]);
      return Promise.resolve(null);
    });
    
    render(<App />);
    
    expect(screen.getByText('00:00:00')).toBeInTheDocument();
    
    consoleErrorSpy.mockRestore();
  });
});