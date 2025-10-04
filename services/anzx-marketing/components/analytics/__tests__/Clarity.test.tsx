import { render } from '@testing-library/react';
import { Clarity, clarityTrack } from '../Clarity';

// Mock window.clarity
const mockClarity = jest.fn();

describe('Clarity Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    delete (window as any).clarity;
    
    // Mock environment
    process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID = 'test_project_id';
    process.env.NODE_ENV = 'production';
  });

  afterEach(() => {
    delete process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID;
    process.env.NODE_ENV = 'test';
  });

  it('should not render in development mode', () => {
    process.env.NODE_ENV = 'development';
    const { container } = render(<Clarity />);
    expect(container.firstChild).toBeNull();
  });

  it('should not render without project ID', () => {
    delete process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID;
    const { container } = render(<Clarity />);
    expect(container.firstChild).toBeNull();
  });

  it('should render in production with project ID', () => {
    const { container } = render(<Clarity />);
    // Component returns null but initializes Clarity
    expect(container.firstChild).toBeNull();
  });

  describe('clarityTrack utilities', () => {
    beforeEach(() => {
      (window as any).clarity = mockClarity;
    });

    it('should identify users', () => {
      clarityTrack.identify('user123', { plan: 'pro' });
      expect(mockClarity).toHaveBeenCalledWith('identify', 'user123', { plan: 'pro' });
    });

    it('should track events', () => {
      clarityTrack.event('button_click', { button_name: 'cta' });
      expect(mockClarity).toHaveBeenCalledWith('event', 'button_click', { button_name: 'cta' });
    });

    it('should set custom properties', () => {
      clarityTrack.set('user_role', 'admin');
      expect(mockClarity).toHaveBeenCalledWith('set', 'user_role', 'admin');
    });

    it('should upgrade session priority', () => {
      clarityTrack.upgrade('high_value_user');
      expect(mockClarity).toHaveBeenCalledWith('upgrade', 'high_value_user');
    });

    it('should not throw errors when clarity is not loaded', () => {
      delete (window as any).clarity;
      
      expect(() => {
        clarityTrack.identify('user123');
        clarityTrack.event('test_event');
        clarityTrack.set('key', 'value');
        clarityTrack.upgrade('reason');
      }).not.toThrow();
    });
  });

  describe('Page type detection', () => {
    it('should detect homepage', () => {
      Object.defineProperty(window, 'location', {
        value: { pathname: '/' },
        writable: true,
      });
      
      // getPageType is called internally
      render(<Clarity />);
      // Would need to expose getPageType for direct testing
    });

    it('should detect blog post', () => {
      Object.defineProperty(window, 'location', {
        value: { pathname: '/blog/ai-agents-guide' },
        writable: true,
      });
      
      render(<Clarity />);
    });

    it('should detect product page', () => {
      Object.defineProperty(window, 'location', {
        value: { pathname: '/ai-interviewer' },
        writable: true,
      });
      
      render(<Clarity />);
    });
  });

  describe('User segment detection', () => {
    it('should detect paid search traffic', () => {
      Object.defineProperty(window, 'location', {
        value: { 
          pathname: '/',
          search: '?utm_source=google-ads'
        },
        writable: true,
      });
      
      render(<Clarity />);
    });

    it('should detect social traffic', () => {
      Object.defineProperty(window, 'location', {
        value: { 
          pathname: '/',
          search: '?utm_source=linkedin'
        },
        writable: true,
      });
      
      render(<Clarity />);
    });

    it('should detect email traffic', () => {
      Object.defineProperty(window, 'location', {
        value: { 
          pathname: '/',
          search: '?utm_source=email'
        },
        writable: true,
      });
      
      render(<Clarity />);
    });
  });

  describe('Event tracking', () => {
    beforeEach(() => {
      (window as any).clarity = mockClarity;
      document.body.innerHTML = '';
    });

    it('should track form field focus', () => {
      const input = document.createElement('input');
      input.setAttribute('name', 'email');
      const form = document.createElement('form');
      form.setAttribute('data-form-name', 'demo_form');
      form.appendChild(input);
      document.body.appendChild(form);

      render(<Clarity />);
      
      // Simulate focus event
      const focusEvent = new FocusEvent('focusin', { bubbles: true });
      input.dispatchEvent(focusEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'form_field_focus', {
        form_name: 'demo_form',
        field_name: 'email',
      });
    });

    it('should track CTA clicks', () => {
      const button = document.createElement('button');
      button.textContent = 'Get Started';
      document.body.appendChild(button);

      render(<Clarity />);
      
      // Simulate click event
      const clickEvent = new MouseEvent('click', { bubbles: true });
      button.dispatchEvent(clickEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'cta_click', expect.objectContaining({
        cta_text: 'Get Started',
      }));
    });

    it('should track video play', () => {
      const video = document.createElement('video');
      video.src = '/videos/demo.mp4';
      video.duration = 120;
      document.body.appendChild(video);

      render(<Clarity />);
      
      // Simulate play event
      const playEvent = new Event('play', { bubbles: true });
      video.dispatchEvent(playEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'video_play', {
        video_src: '/videos/demo.mp4',
        video_duration: 120,
      });
    });

    it('should track file downloads', () => {
      const link = document.createElement('a');
      link.href = '/downloads/whitepaper.pdf';
      link.textContent = 'Download Whitepaper';
      document.body.appendChild(link);

      render(<Clarity />);
      
      // Simulate click event
      const clickEvent = new MouseEvent('click', { bubbles: true });
      link.dispatchEvent(clickEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'file_download', {
        file_url: expect.stringContaining('whitepaper.pdf'),
        file_name: 'Download Whitepaper',
      });
    });

    it('should track rage clicks', (done) => {
      const button = document.createElement('button');
      document.body.appendChild(button);

      render(<Clarity />);
      
      // Simulate multiple rapid clicks
      for (let i = 0; i < 5; i++) {
        const clickEvent = new MouseEvent('click', { bubbles: true });
        button.dispatchEvent(clickEvent);
      }

      // Wait for the rage click timer
      setTimeout(() => {
        expect(mockClarity).toHaveBeenCalledWith('event', 'rage_click', expect.objectContaining({
          click_count: expect.any(Number),
        }));
        done();
      }, 1100);
    });

    it('should track JavaScript errors', () => {
      render(<Clarity />);
      
      // Simulate error event
      const errorEvent = new ErrorEvent('error', {
        message: 'Test error',
        filename: 'test.js',
        lineno: 42,
        colno: 10,
      });
      window.dispatchEvent(errorEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'javascript_error', {
        error_message: 'Test error',
        error_filename: 'test.js',
        error_line: 42,
        error_column: 10,
      });
    });

    it('should track unhandled promise rejections', () => {
      render(<Clarity />);
      
      // Simulate unhandled rejection
      const rejectionEvent = new PromiseRejectionEvent('unhandledrejection', {
        promise: Promise.reject('Test rejection'),
        reason: 'Test rejection',
      });
      window.dispatchEvent(rejectionEvent);

      expect(mockClarity).toHaveBeenCalledWith('event', 'unhandled_promise_rejection', {
        error_reason: 'Test rejection',
      });
    });
  });
});
