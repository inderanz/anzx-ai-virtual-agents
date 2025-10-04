import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';

describe('LanguageSwitcher', () => {
  it('renders language switcher', () => {
    render(<LanguageSwitcher />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows current language', () => {
    render(<LanguageSwitcher />);
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent(/en|hi/i);
  });

  it('toggles language menu on click', () => {
    render(<LanguageSwitcher />);
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    // Menu should be visible
    expect(screen.getByText(/english|hindi/i)).toBeInTheDocument();
  });
});
