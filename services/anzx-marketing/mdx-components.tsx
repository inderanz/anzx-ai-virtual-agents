import type { MDXComponents } from 'mdx/types';
import Image from 'next/image';
import Link from 'next/link';

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // Override default HTML elements with custom components
    h1: ({ children }) => {
      const id = typeof children === 'string' 
        ? children.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').trim()
        : '';
      return (
        <h1 id={id} className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white mb-6 mt-8">
          {children}
        </h1>
      );
    },
    h2: ({ children }) => {
      const id = typeof children === 'string' 
        ? children.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').trim()
        : '';
      return (
        <h2 id={id} className="text-3xl font-semibold tracking-tight text-gray-900 dark:text-white mb-4 mt-8">
          {children}
        </h2>
      );
    },
    h3: ({ children }) => {
      const id = typeof children === 'string' 
        ? children.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').trim()
        : '';
      return (
        <h3 id={id} className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white mb-3 mt-6">
          {children}
        </h3>
      );
    },
    h4: ({ children }) => {
      const id = typeof children === 'string' 
        ? children.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').trim()
        : '';
      return (
        <h4 id={id} className="text-xl font-semibold text-gray-900 dark:text-white mb-2 mt-4">
          {children}
        </h4>
      );
    },
    p: ({ children }) => (
      <p className="text-lg leading-relaxed text-gray-700 dark:text-gray-300 mb-4">
        {children}
      </p>
    ),
    a: ({ href, children }) => (
      <Link
        href={href || '#'}
        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
      >
        {children}
      </Link>
    ),
    ul: ({ children }) => (
      <ul className="list-disc list-inside space-y-2 mb-4 text-gray-700 dark:text-gray-300">
        {children}
      </ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-700 dark:text-gray-300">
        {children}
      </ol>
    ),
    li: ({ children }) => (
      <li className="mb-1">{children}</li>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 dark:text-gray-400 mb-4">
        {children}
      </blockquote>
    ),
    code: ({ children }) => (
      <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono">
        {children}
      </code>
    ),
    pre: ({ children }) => (
      <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg overflow-x-auto mb-4">
        {children}
      </pre>
    ),
    ...components,
  };
}