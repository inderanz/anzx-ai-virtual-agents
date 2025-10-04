import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getTranslations } from 'next-intl/server';
import ArticleLayout from '@/components/blog/ArticleLayout';
import { getBlogPost, getAllBlogPosts, getRelatedPosts } from '@/lib/blog';
import { routing } from '@/routing';

interface BlogPostPageProps {
  params: {
    locale: string;
    slug: string;
  };
}

export async function generateStaticParams() {
  const posts = await getAllBlogPosts();
  // Use routing.locales instead
  
  // Generate all combinations of locale and slug
  const params = [];
  for (const locale of routing.locales) {
    for (const post of posts) {
      params.push({
        locale,
        slug: post.slug,
      });
    }
  }
  
  return params;
}

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const post = await getBlogPost(params.slug);
  
  if (!post) {
    return {
      title: 'Post Not Found',
    };
  }

  return {
    title: `${post.title} | ANZX.ai Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt.toISOString(),
      modifiedTime: post.updatedAt?.toISOString(),
      authors: [post.author],
      images: [
        {
          url: post.featuredImage,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: [post.featuredImage],
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const post = await getBlogPost(params.slug);
  
  if (!post) {
    notFound();
  }

  const relatedPosts = await getRelatedPosts(post, 3);

  return <ArticleLayout post={post} relatedPosts={relatedPosts} />;
}
