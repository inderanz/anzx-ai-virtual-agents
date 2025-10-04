import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock form component
const MockDemoForm = () => {
  const [submitted, setSubmitted] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 100));
    setSubmitted(true);
  };

  if (submitted) {
    return <div>Thank you for your submission!</div>;
  }

  return (
    <form onSubmit={handleSubmit} data-testid="demo-form">
      <input
        type="text"
        name="name"
        placeholder="Name"
        required
        data-testid="name-input"
      />
      <input
        type="email"
        name="email"
        placeholder="Email"
        required
        data-testid="email-input"
      />
      <button type="submit" data-testid="submit-button">
        Submit
      </button>
    </form>
  );
};

describe('Form Submission Integration', () => {
  it('submits form successfully', async () => {
    const user = userEvent.setup();
    render(<MockDemoForm />);

    const nameInput = screen.getByTestId('name-input');
    const emailInput = screen.getByTestId('email-input');
    const submitButton = screen.getByTestId('submit-button');

    await user.type(nameInput, 'John Doe');
    await user.type(emailInput, 'john@example.com');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/thank you/i)).toBeInTheDocument();
    });
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(<MockDemoForm />);

    const submitButton = screen.getByTestId('submit-button');
    await user.click(submitButton);

    // Form should not submit without required fields
    expect(screen.queryByText(/thank you/i)).not.toBeInTheDocument();
  });
});
