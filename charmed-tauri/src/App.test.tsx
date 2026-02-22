import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';

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

  it('renders clock', () => {
    render(<App />);
    
    expect(screen.getByText('00:00:00')).toBeInTheDocument();
  });

  it('shows Inactif status when no alarms are active', () => {
    render(<App />);
    expect(screen.getByText('Inactif')).toBeInTheDocument();
  });

  it('renders the time input with default value', () => {
    render(<App />);
    expect(screen.getByDisplayValue('08:00')).toBeInTheDocument();
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

  it('creates a new alarm when set button is clicked', async () => {
    mockInvoke.mockImplementation((cmd: string) => {
      if (cmd === 'get_current_time') return Promise.resolve('12:00:00');
      if (cmd === 'check_alarms') return Promise.resolve(null);
      if (cmd === 'get_alarms') return Promise.resolve([]);
      if (cmd === 'set_alarm') return Promise.resolve(null);
      return Promise.resolve(null);
    });
    
    render(<App />);
    
    const buttons = screen.getAllByRole('button');
    const alarmButton = buttons.find(btn => btn.className.includes('bg-[#1DB954]'));
    
    if (alarmButton) {
      fireEvent.click(alarmButton);
      
      await waitFor(() => {
        expect(mockInvoke).toHaveBeenCalledWith('set_alarm', expect.objectContaining({
          time: '08:00'
        }));
      });
    }
  });

  it('changes alarm time when input value changes', () => {
    render(<App />);
    
    const timeInput = screen.getByDisplayValue('08:00');
    fireEvent.change(timeInput, { target: { value: '09:30' } });
    
    expect(timeInput).toHaveValue('09:30');
  });

  it('handles set_alarm error gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    mockInvoke.mockImplementation((cmd: string) => {
      if (cmd === 'get_current_time') return Promise.resolve('12:00:00');
      if (cmd === 'check_alarms') return Promise.resolve(null);
      if (cmd === 'get_alarms') return Promise.resolve([]);
      if (cmd === 'set_alarm') return Promise.reject(new Error('Set alarm failed'));
      return Promise.resolve(null);
    });
    
    render(<App />);
    
    const buttons = screen.getAllByRole('button');
    const alarmButton = buttons.find(btn => btn.className.includes('bg-[#1DB954]'));
    
    if (alarmButton) {
      fireEvent.click(alarmButton);
    }
    
    consoleErrorSpy.mockRestore();
  });

  it('renders the header with logo', () => {
    render(<App />);
    
    // Check for logo and title
    expect(screen.getByText('Charmed')).toBeInTheDocument();
    expect(screen.getByText('Spotify Alarm Clock')).toBeInTheDocument();
  });

  it('renders glass-panel containers', () => {
    render(<App />);
    
    const glassPanels = document.querySelectorAll('.glass-panel');
    expect(glassPanels.length).toBeGreaterThan(0);
  });

  it('renders gradient background', () => {
    render(<App />);
    
    const gradientBg = document.querySelector('.gradient-bg');
    expect(gradientBg).toBeInTheDocument();
  });

  it('renders status indicator', () => {
    render(<App />);
    
    // The status indicator shows "Inactif" when no alarms
    expect(screen.getByText('Inactif')).toBeInTheDocument();
  });

  it('renders Spotify connect button', () => {
    render(<App />);
    
    expect(screen.getByText('Connecter Spotify')).toBeInTheDocument();
  });
});