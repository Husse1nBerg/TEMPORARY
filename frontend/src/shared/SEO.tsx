// While Next.js 13+ prefers static metadata exports,
// this component can be useful for pages where SEO tags are highly dynamic.
import Head from 'next/head';

interface SEOProps {
  title: string;
  description: string;
  keywords?: string;
  ogImage?: string;
}

export default function SEO({ title, description, keywords, ogImage }: SEOProps) {
  const siteTitle = `CROPS Price Tracker | ${title}`;
  return (
    <Head>
      <title>{siteTitle}</title>
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      <meta property="og:title" content={siteTitle} />
      <meta property="og:description" content={description} />
      {ogImage && <meta property="og:image" content={ogImage} />}
    </Head>
  );
}