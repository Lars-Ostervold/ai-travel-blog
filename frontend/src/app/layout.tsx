import Footer from "@/app/_components/footer";
import { SITE_URL, HOME_OG_IMAGE_URL, BLOG_TITLE} from "@/lib/constants";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import cn from "classnames";
import { ThemeSwitcher } from "./_components/theme-switcher";

import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: `${BLOG_TITLE}`,
  description: `Join Audrey, a fun-loving, adventurous mom, as she travels the world with her husband Noah and their two young boys, Leo and Max. Audrey shares engaging, humorous, and informative stories about their family adventures, offering honest insights into the challenges and joys of traveling with kids. Her goal is to inspire other young families to explore the world and create unforgettable memories together. Discover tips, advice, and personal anecdotes that will help you plan your next family trip.`,
  openGraph: {
    images: [HOME_OG_IMAGE_URL],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/favicon/apple-touch-icon.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon/favicon-16x16.png"
        />
        <link rel="manifest" href="/favicon/site.webmanifest" />
        <link
          rel="mask-icon"
          href="/favicon/safari-pinned-tab.svg"
          color="#000000"
        />
        <link rel="shortcut icon" href="/favicon/favicon.ico" />
        <meta name="msapplication-TileColor" content="#000000" />
        <meta
          name="msapplication-config"
          content="/favicon/browserconfig.xml"
        />
        <meta name="theme-color" content="#000" />
        <link rel="alternate" type="application/rss+xml" href="/feed.xml" />
        <meta name="description" content="Join Audrey, a fun-loving, adventurous mom, as she travels the world with her husband Noah and their two young boys, Leo and Max. Audrey shares engaging, humorous, and informative stories about their family adventures, offering honest insights into the challenges and joys of traveling with kids. Her goal is to inspire other young families to explore the world and create unforgettable memories together. Discover tips, advice, and personal anecdotes that will help you plan your next family trip." />
        <meta name="keywords" content="travel, family travel, travel with kids, travel blog, family adventures, travel tips" />
        <meta name="robots" content="index, follow" />
        <meta name="author" content="Audrey Rose" />
        <meta property="og:title" content={`${BLOG_TITLE}`} />
        <meta property="og:description" content="Join Audrey, a fun-loving, adventurous mom, as she travels the world with her husband Noah and their two young boys, Leo and Max. Audrey shares engaging, humorous, and informative stories about their family adventures, offering honest insights into the challenges and joys of traveling with kids. Her goal is to inspire other young families to explore the world and create unforgettable memories together. Discover tips, advice, and personal anecdotes that will help you plan your next family trip." />
        <meta property="og:image" content={HOME_OG_IMAGE_URL} />
        <meta property="og:url" content={`${SITE_URL}`} />
        <meta property="og:type" content="website" />
      </head>
      <body
        className={cn(inter.className, "dark:bg-slate-900 dark:text-slate-400")}
      >
        <ThemeSwitcher />
        <div className="min-h-screen">{children}</div>
        <Footer />
      </body>
    </html>
  );
}
