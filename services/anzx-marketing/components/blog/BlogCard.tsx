import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { OptimizedImage } from '@/components/ui/OptimizedImage';
import { BlogPost } from '@/lib/types/blog';

interface BlogCardProps {
  post: BlogPost;
}

export default function BlogCard({ post }: BlogCardProps) {
  const t = useTranslations('blog');

  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <Link href={`/blog/${post.slug}`}>
        <div className="aspect-video relative overflow-hidden">
          <OptimizedImage
            src={post.featuredImage}
            alt={post.title}
            width={400}
            height={225}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          />
        </div>
      </Link>
      
      <div className="p-6">
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
            {t(`categories.${post.category}`)}
          </span>
          <time dateTime={post.publishedAt.toISOString()}>
            {post.publishedAt.toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </time>
          <span>{post.readingTime} {t('readingTime')}</span>
        </div>
        
        <Link href={`/blog/${post.slug}`}>
          <h2 className="text-xl font-semibold text-gray-900 mb-3 hover:text-blue-600 transition-colors line-clamp-2">
            {post.title}
          </h2>
        </Link>
        
        <p className="text-gray-600 mb-4 line-clamp-3">
          {post.excerpt}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-600">
                {post.author.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="text-sm text-gray-700">{post.author}</span>
          </div>
          
          <Link
            href={`/blog/${post.slug}`}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {t('readMore')} →
          </Link>
        </div>
      </div>
    </article>
  );
}