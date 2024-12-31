# Frontend for AI Travel Blog
**Portions of this README are copied from the Next.js [template](https://github.com/vercel/next.js/tree/canary/examples/blog-starter)**

Frontend uses a [template](https://github.com/vercel/next.js/tree/canary/examples/blog-starter) from Next.js, built with Typescript.

Uses [static generation](https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates) feature using Markdown files as the data source.

The blog posts are stored in `/_posts` as Markdown files with front matter support. Adding a new Markdown file in there will create a new blog post.

Blog posts are created using [`remark`](https://github.com/remarkjs/remark) and [`remark-html`](https://github.com/remarkjs/remark-html) to convert the Markdown files into an HTML string, and then send it down as a prop to the page. The metadata of every post is handled by [`gray-matter`](https://github.com/jonschlinkert/gray-matter) and also sent in props to the page.

## Run the frontend locally

Make sure you are in the frontend/ folder. Then run:

```bash
npm install
```

to install packages. Then run:

```bash
npm run dev
```

and it should be running on localhost:3000.

# Notes

`blog-starter` uses [Tailwind CSS](https://tailwindcss.com) [(v3.0)](https://tailwindcss.com/blog/tailwindcss-v3).
