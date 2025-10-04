'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ArrowLeft, Clock, Calendar, User, Share2, Twitter, Facebook, Linkedin } from 'lucide-react';
import { OptimizedImage } from '@/components/ui/OptimizedImage';
import TableOfContents from './TableOfContents';
import RelatedPosts from './RelatedPosts';
import { BlogPost } from '@/lib/types/blog';
import { MDXRemote } from 'next-mdx-remote/rsc';

interface ArticleLayoutProps {
  post: BlogPost;
  relatedPosts: BlogPost[];
}

export default function ArticleLayout({ post, relatedPosts }: ArticleLayoutProps) {
  const t = useTranslations('blog');
  
  const shareUrl = typeof window !== 'undefined' ? window.location.href : '';
  const shareText = `${post.title} - ${post.excerpt}`;

  const handleShare = (platform: string) => {
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
    };
    
    if (urls[platform as keyof typeof urls]) {
      window.open(urls[platform as keyof typeof urls], '_blank', 'width=600,height=400');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gray-50 border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link
            href="/blog"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('backToBlog')}
          </Link>
          
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
              {t(`categories.${post.category}`)}
            </span>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <time dateTime={post.publishedAt.toISOString()}>
                {post.publishedAt.toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </time>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{post.readingTime} {t('readingTime')}</span>
            </div>
            <div className="flex items-center gap-1">
              <User className="w-4 h-4" />
              <span>{post.author}</span>
            </div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
            {post.title}
          </h1>
          
          <p className="text-xl text-gray-600 mt-4 leading-relaxed">
            {post.excerpt}
          </p>
        </div>
      </div>

      {/* Featured Image */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="aspect-video relative overflow-hidden rounded-lg">
          <OptimizedImage
            src={post.featuredImage}
            alt={post.title}
            width={800}
            height={450}
            className="w-full h-full object-cover"
            priority
          />
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Table of Contents - Desktop */}
          <div className="hidden lg:block lg:col-span-1">
            <div className="sticky top-8">
              <TableOfContents content={post.content} />
            </div>
          </div>
          
          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Table of Contents - Mobile */}
            <div className="lg:hidden mb-8">
              <TableOfContents content={post.content} />
            </div>
            
            {/* Article Body */}
            <article className="prose prose-lg max-w-none">
              <MDXRemote source={post.content} />
            </article>
            
            {/* Tags */}
            {post.tags.length > 0 && (
              <div className="mt-12 pt-8 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('tags')}</h3>
                <div className="flex flex-wrap gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* Share Buttons */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Share2 className="w-5 h-5" />
                {t('shareArticle')}
              </h3>
              <div className="flex gap-4">
                <button
                  onClick={() => handleShare('twitter')}
                  className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Twitter className="w-4 h-4" />
                  Twitter
                </button>
                <button
                  onClick={() => handleShare('facebook')}
                  className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg hover:bg-blue-800 transition-colors"
                >
                  <Facebook className="w-4 h-4" />
                  Facebook
                </button>
                <button
                  onClick={() => handleShare('linkedin')}
                  className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Linkedin className="w-4 h-4" />
                  LinkedIn
                </button>
              </div>
            </div>
            
            {/* Author Bio */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                  <span className="text-xl font-semibold text-gray-600">
                    {post.author.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{post.author}</h3>
                  <p className="text-gray-600 mt-1">
                    {t('authorBio', { author: post.author })}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Related Posts */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <RelatedPosts currentPost={post} relatedPosts={relatedPosts} />
        </div>
      </div>
      
      {/* Back to Blog CTA */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <Link
            href="/blog"
            className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('backToBlog')}
          </Link>
        </div>
      </div>
    </div>
  );
}