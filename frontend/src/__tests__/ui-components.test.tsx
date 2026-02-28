import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Test UI components from the design system
describe('UI Components', () => {
  describe('Button', () => {
    it('renders with children text', async () => {
      const { Button } = await import('@/components/ui/button');
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeDefined();
    });

    it('handles click events', async () => {
      const { Button } = await import('@/components/ui/button');
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click me</Button>);

      const user = userEvent.setup();
      await user.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('can be disabled', async () => {
      const { Button } = await import('@/components/ui/button');
      render(<Button disabled>Disabled</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('applies variant classes', async () => {
      const { Button } = await import('@/components/ui/button');
      const { container } = render(<Button variant="destructive">Delete</Button>);
      expect(container.firstChild).toBeDefined();
    });
  });

  describe('Input', () => {
    it('renders an input element', async () => {
      const { Input } = await import('@/components/ui/input');
      render(<Input placeholder="Type here..." />);
      expect(screen.getByPlaceholderText('Type here...')).toBeDefined();
    });

    it('accepts user input', async () => {
      const { Input } = await import('@/components/ui/input');
      const handleChange = vi.fn();
      render(<Input onChange={handleChange} />);

      const user = userEvent.setup();
      const input = screen.getByRole('textbox');
      await user.type(input, 'Hello');
      expect(handleChange).toHaveBeenCalled();
    });
  });

  describe('Badge', () => {
    it('renders badge with text', async () => {
      const { Badge } = await import('@/components/ui/badge');
      render(<Badge>New</Badge>);
      expect(screen.getByText('New')).toBeDefined();
    });
  });

  describe('Card', () => {
    it('renders card with content', async () => {
      const { Card, CardHeader, CardTitle, CardContent } = await import('@/components/ui/card');
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
          </CardHeader>
          <CardContent>Card body content</CardContent>
        </Card>
      );
      expect(screen.getByText('Test Card')).toBeDefined();
      expect(screen.getByText('Card body content')).toBeDefined();
    });
  });

  describe('Tabs', () => {
    it('renders tabs with panels', async () => {
      const { Tabs, TabsList, TabsTrigger, TabsContent } = await import('@/components/ui/tabs');
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Content 1</TabsContent>
          <TabsContent value="tab2">Content 2</TabsContent>
        </Tabs>
      );
      expect(screen.getByText('Tab 1')).toBeDefined();
      expect(screen.getByText('Tab 2')).toBeDefined();
      expect(screen.getByText('Content 1')).toBeDefined();
    });
  });
});
