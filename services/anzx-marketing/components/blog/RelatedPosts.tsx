'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { OptimizedImage } from '@/components/ui/OptimizedImage';
import { BlogPost } from '@/lib/types/blog';
interface RelatedPostsProps {
  currentPost: BlogPost;
  relatedPosts: BlogPost[];
  maxPosts?: number;
}

export default function RelatedPosts({ currentPost, relatedPosts, maxPosts = 3 }: RelatedPostsProps) {
  const t = useTranslations('blog');

  if (relatedPosts.length === 0) {
    return null;
  }

  return (
    <div className="mt-16 pt-8 border-t border-gray-200">
      <h3 className="text-2xl font-bold text-gray-900 mb-8">{t('relatedPosts')}</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {relatedPosts.map((post) => (
          <article key={post.slug} className="group">
            <Link href={`/blog/${post.slug}`}>
              <div className="aspect-video relative overflow-hidden rounded-lg mb-4">
                <OptimizedImage
                  src={post.featuredImage}
                  alt={post.title}
                  width={300}
                  height={169}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
            </Link>
            
            <div className="space-y-2">
              <div className="flex items-center gap-3 text-sm text-gray-500">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                  {t(`categories.${post.category}`)}
                </span>
                <time dateTime={post.publishedAt.toISOString()}>
                  {post.publishedAt.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </time>
              </div>
              
              <Link href={`/blog/${post.slug}`}>
                <h4 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
                  {post.title}
                </h4>
              </Link>
              
              <p className="text-gray-600 text-sm line-clamp-2">
                {post.excerpt}
              </p>
              
              <div className="flex items-center justify-between pt-2">
                <span className="text-sm text-gray-500">{post.readingTime} {t('readingTime')}</span>
                <Link
                  href={`/blog/${post.slug}`}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {t('readMore')} →
                </Link>
              </div>
            </div>
          </article>
        ))}
      </div>
      
      {/* CTA Section */}
      <div className="mt-12 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
        <div className="text-center">
          <h4 className="text-xl font-semibold text-gray-900 mb-2">
            {t('cta.title')}
          </h4>
          <p className="text-gray-600 mb-4">
            {t('cta.description')}
          </p>
          <Link
            href="/get-started"
            className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {t('cta.button')}
          </Link>
        </div>
      </div>
    </div>
  );
}